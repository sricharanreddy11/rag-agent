from datetime import datetime
from enum import Enum

from core.services.llm_interface import LLMInterface
from university_agent.models import ChatSession
from university_agent.serializers import ChatSessionDetailSerializer, TaskSerializer


def get_previous_context_from_session(session_id: str):
    try:
        session_obj = ChatSession.objects.filter(session_id=session_id).first()
        session_data = ChatSessionDetailSerializer(session_obj).data
        previous_conversation = []
        messages = session_data.get('messages')
        for message in messages:
            previous_conversation.append({
                "role": message.get('role'),
                "content": message.get('content')
            })
        return previous_conversation
    except Exception as e:
        return []

def identify_creation_intent_and_execute(user_query):
    """
    Identify the intent of the user query and execute the corresponding action.

    :param user_query: str - The user's query or command.
    :return: str - The result of the identified action.
    """

    from pydantic import BaseModel
    from typing import Optional
    import json

    class TaskStatus(str, Enum):
        todo = 'todo'
        completed = 'completed'

    class TaskPriority(str, Enum):
        low = 'low'
        medium = 'medium'
        high = 'high'

    class Task(BaseModel):
        creation_intent: bool
        assistant_message: str
        title: str
        description: Optional[str] = None
        due_date: Optional[str] = None
        status: TaskStatus
        priority: TaskPriority

    user_query = f"Current Datetime; {datetime.now()} User Query:{user_query}"

    content = LLMInterface().get_custom_structured_response(
        config_name="task-creation-agent",
        user_prompt=user_query,
        response_format=Task,
    )

    task_dict = json.loads(content.choices[0].message.content)
    creation_intent = task_dict.pop('creation_intent')
    assistant_message = task_dict.pop('assistant_message')
    if creation_intent:
        serializer = TaskSerializer(data=task_dict)
        serializer.is_valid(raise_exception=True)
        task_obj = serializer.save()
        return True, assistant_message

    else:
        return False, assistant_message

