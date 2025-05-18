import json
import os
import qdrant_client
import openai
from qdrant_client.http import models
import uuid
import logging
from typing import List, Dict, Optional
import re
import requests
from core.services.llm_interface import LLMInterface
from university_agent.utils import get_previous_context_from_session, identify_creation_intent_and_execute

logger = logging.getLogger(__name__)


class QdrantServiceError(Exception):
    """Base exception for Qdrant service errors"""
    pass


class QdrantRAGAgent:
    def __init__(self, collection_name: str = "newStudents"):
        try:
            self.QDRANT_URL = os.environ.get("QDRANT_URL")
            self.QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")

            if not self.QDRANT_URL or not self.QDRANT_API_KEY:
                raise QdrantServiceError(
                    "Missing Qdrant configuration. Please check QDRANT_URL and QDRANT_API_KEY environment variables.")

            self.client = qdrant_client.QdrantClient(url=self.QDRANT_URL, api_key=self.QDRANT_API_KEY)
            self.openai_client = openai.OpenAI()
            self.collection_name = collection_name
            # self.knowledge_base = config.meta_data.get("knowledge_base", [])

            openai_api_key = os.environ.get("OPENAI_API_KEY")
            if not openai_api_key:
                raise QdrantServiceError("Missing OpenAI API key. Please check OPENAI_API_KEY environment variable.")

            self.openai_client.api_key = openai_api_key
        except Exception as e:
            logger.error(f"Failed to initialize QdrantRAGAgent: {str(e)}")
            raise QdrantServiceError(f"Initialization failed: {str(e)}")

    def search_qdrant_api(
            self,
            query_vector: List[float],
            collection_name: str,
            limit: int = 3,
            score_threshold: float = 0.7
    ):
        """
        Search Qdrant using direct REST API calls instead of the client library.
        This may help bypass Windows-specific network issues.
        """
        qdrant_url = os.environ.get("QDRANT_URL")
        qdrant_api_key = os.environ.get("QDRANT_API_KEY")

        if not qdrant_url.endswith('/'):
            qdrant_url += '/'

        search_url = f"{qdrant_url}collections/{collection_name}/points/search"

        print(search_url)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if qdrant_api_key:
            headers["api-key"] = qdrant_api_key

        payload = {
            "vector": query_vector,
            "limit": limit,
            "score_threshold": score_threshold,
            "with_payload": True
        }

        try:
            response = requests.post(
                search_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=60  # Set a generous timeout
            )

            response.raise_for_status()  # Raise an exception for 4XX/5XX responses

            result = response.json()
            return result.get("result", [])
        except QdrantServiceError as e:
            logger.error(f"Qdrant API request error: {str(e)}")
            raise Exception(f"Failed to search Qdrant via API: {str(e)}")

    def get_context_from_vector_db_api(self, user_query: str, n_points: int = 3, score_threshold: float = 0.7) -> str:
        if not user_query:
            logger.warning("Empty user query provided")
            return ""

        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=user_query
            )
            query_vector = response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"Failed to generate embeddings: {str(e)}")

        print("Searching Qdrant via API")
        try:
            # Use the API search function instead of client library
            vector_results = self.search_qdrant_api(
                query_vector=query_vector,
                collection_name=self.collection_name,
                limit=n_points,
                score_threshold=score_threshold
            )
        except Exception as e:
            logger.error(f"Qdrant API search error: {str(e)}")
            raise Exception(f"Failed to search vector database via API: {str(e)}")

        if not vector_results:
            logger.warning("No results found in vector API search")
            return ""

        if len(vector_results) == 1:
            return vector_results[0].get('payload', {}).get('context', "")

        context_parts = []
        for r in vector_results:
            context_parts.append(f"""{r.get('payload', {}).get('context', "")}
                                        """)

        context = "\n\n".join(context_parts)
        return context

    def create_collection(self, knowledge_base):
        self._ensure_collection_exists()
        self._populate_collection(knowledge_base)

    def _ensure_collection_exists(self):
        """Create the Qdrant collection if it doesn't exist."""
        try:
            self.client.get_collection(self.collection_name)
            print(f"Collection {self.collection_name} already exists")
        except Exception as e:
            print(f"Creating collection {self.collection_name}...")
            try:
                self.client.recreate_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=1536,
                        distance=models.Distance.COSINE
                    )
                )
                print("Collection created successfully")
            except Exception as e:
                logger.error(f"Failed to create collection: {str(e)}")
                raise QdrantServiceError(f"Failed to create collection: {str(e)}")

    def _populate_collection(self, knowledge_base):
        """Populate the Qdrant collection with meeting data."""
        print("Starting collection population...")

        try:
            collection_info = self.client.get_collection(self.collection_name)
        except Exception as e:
            logger.error(f"Error checking collection: {str(e)}")
            raise QdrantServiceError(f"Failed to check collection: {str(e)}")

        try:
            if not knowledge_base:
                logger.warning("No knowledge base entries found in configuration")
                return
        except Exception as e:
            logger.error(f"Failed to fetch knowledge base configuration: {str(e)}")
            raise QdrantServiceError(f"Failed to fetch knowledge base: {str(e)}")

        points = []
        for i, kb in enumerate(knowledge_base):
            try:
                text_to_embed = f'''
                {kb}
                '''

                try:
                    vector = self.openai_client.embeddings.create(
                        model="text-embedding-ada-002",
                        input=text_to_embed
                    ).data[0].embedding
                except Exception as e:
                    logger.error(f"OpenAI API error for kb {i}: {str(e)}")
                    continue

                point_id = str(uuid.uuid4())
                points.append(models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        'context': kb
                    }
                ))

                if (i + 1) % 100 == 0:
                    print(f"Processed {i + 1} kb...")

            except Exception as e:
                logger.error(f"Error processing kb {i}: {str(e)}")
                continue

        if not points:
            logger.warning("No valid points to insert")
            return

        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                print(f"Inserted batch {i // batch_size + 1} of {len(points) // batch_size + 1}")
            except Exception as e:
                logger.error(f"Error inserting batch: {str(e)}")
                raise QdrantServiceError(f"Failed to insert batch: {str(e)}")

        print("Collection population complete")

    def get_context_from_vector_db(self, user_query: str, n_points: int = 3, score_threshold: float = 0.7) -> str:
        if not user_query:
            logger.warning("Empty user query provided")
            return ""

        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=user_query
            )
            query_vector = response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise QdrantServiceError(f"Failed to generate embeddings: {str(e)}")

        print("Searching Qdrant")
        try:
            vector_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=n_points,
                score_threshold=score_threshold
            )
        except Exception as e:
            logger.error(f"Qdrant search error: {str(e)}")
            raise QdrantServiceError(f"Failed to search vector database: {str(e)}")

        if not vector_results:
            logger.warning("No results found in vector search")
            return ""

        if len(vector_results) == 1:
            return vector_results[0].payload.get('context', "")

        context_parts = []
        for r in vector_results:
            context_parts.append(f"""{r.payload.get('context', "")}
                                        """)

        context = "\n\n".join(context_parts)
        return context

    def get_response_using_rag(self, config_name, user_query: str, n_points: int = 3,
                               previous_context: Optional[List[Dict[str, str]]] = None) -> str:
        if not user_query:
            logger.warning("Empty user query provided")
            return ""

        if previous_context is None:
            previous_context = []

        try:
            context = self.get_context_from_vector_db_api(
                user_query=user_query,
                n_points=n_points
            )
        except QdrantServiceError as e:
            logger.error(f"Failed to get context: {str(e)}")
            context = ""

        try:
            config_obj = LLMInterface().get_config_object(config_name=config_name)
            if not config_obj:
                raise QdrantServiceError("Failed to get RAG messaging agent configuration")
        except Exception as e:
            logger.error(f"Failed to get configuration: {str(e)}")
            return "I apologize, but I'm having trouble accessing the configuration at the moment."

        try:
            system_prompt = config_obj.system_behaviour

            meta_prompt = f'''
            Context to be used: {context.strip()}
            Previous Conversation: {previous_context}
            Current Question: {user_query.strip()}
            Answer:
            '''
        except Exception as e:
            logger.error(f"Failed to format metaprompt: {str(e)}")
            return "I apologize, but I'm having trouble processing your request at the moment."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": meta_prompt}
        ]

        try:
            content = LLMInterface().get_custom_response_from_context(
                messages=messages,
                config_name="university-agent",
            )
            return content
        except Exception as e:
            logger.error(f"Failed to get response from LLM: {str(e)}")
            return "I apologize, but I'm having trouble generating a response at the moment."


    def get_response_for_new_user(self, user_query: str, session_id: Optional[str] = None) -> str:
        try:
            previous_context = []
            if session_id:
                previous_context = get_previous_context_from_session(session_id)

            response = self.get_response_using_rag(
                user_query=user_query,
                n_points=2,
                previous_context=previous_context,
                config_name='university-agent'
            )
            return response
        except Exception as e:
            logger.error(f"Failed to get response for rag agent: {str(e)}")
            return "I apologize, but I'm having trouble processing your request at the moment."


    def get_response_for_existing_user(self, user_query: str, session_id: Optional[str] = None) -> str:
        try:
            previous_context = []
            creation_intent, response = identify_creation_intent_and_execute(user_query=user_query)
            if creation_intent:
                return response
            if session_id:
                previous_context = get_previous_context_from_session(session_id)

            response = self.get_response_using_rag(
                user_query=user_query,
                n_points=1,
                previous_context=previous_context,
                config_name='university-agent'
            )
            return response
        except Exception as e:
            logger.error(f"Failed to get response for rag agent: {str(e)}")
            return "I apologize, but I'm having trouble processing your request at the moment."

    def get_response_for_tutor(self, user_query: str, user_details = None, user_level = "medium") -> str:

        user_query = f"User Details: {user_details}\n User Level: {user_level}\n User Query: {user_query}"
        try:
            context_dict = self.get_context_from_vector_db_api(
                user_query=user_query,
                n_points=1
            )
            if not context_dict:
                context_dict = {
                    "description": "There is no relevant context available for this query.",
                }
            link = 'https://anurag.edu.in'
            if isinstance(context_dict, dict):
                link = context_dict.pop('link', "")

            def clean_json_response(raw_content: str):
                return re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_content.strip())

            content = LLMInterface().get_custom_response(
                config_name="tutor-agent",
                user_prompt=user_query,
            )
            if not content:
                response_dict = {}
            else:
                cleaned = clean_json_response(content)
                response_dict = json.loads(cleaned)

            response_dict['link'] = link
            return response_dict
        except Exception as e:
            logger.error(f"Failed to get response for rag agent: {str(e)}")
            return "I apologize, but I'm having trouble processing your request at the moment."