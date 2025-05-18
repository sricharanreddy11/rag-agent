from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from core.services.qdrant_service import QdrantRAGAgent
from university_agent.models import ChatSession, ChatMessage, Task
from university_agent.serializers import ChatSessionDetailSerializer, \
    ChatSessionListSerializer, TaskSerializer


class ChatSessionAPI(viewsets.ModelViewSet):
    serializer_class = ChatSessionListSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChatSessionDetailSerializer
        return ChatSessionListSerializer

    def get_queryset(self):
        return ChatSession.objects.filter(is_active=True)

    @action(methods=["POST"], detail=False, url_path="send-message")
    def send_message(self, request, pk=None):
        data = request.data
        session_id = data.get('session_id')
        user_query = data.get('user_query')
        if session_id:
            session_obj = ChatSession.objects.filter(session_id=session_id).first()
        else:
            session_obj = None
        if not session_obj:
            session_obj = ChatSession.objects.create(
                name='Untitled'
            )

        user_message = ChatMessage.objects.create(
            session=session_obj,
            role='user',
            content=user_query
        )

        rag_agent = QdrantRAGAgent()
        response = rag_agent.get_response_for_existing_user(user_message.content, str(session_obj.session_id))

        assistant_message = ChatMessage.objects.create(
            session=session_obj,
            role='assistant',
            content=response
        )

        session_obj.refresh_from_db()

        response = ChatSessionDetailSerializer(session_obj).data

        return Response(response, status=HTTP_200_OK)



class TempSessionAPI(viewsets.ModelViewSet):
    serializer_class = ChatSessionListSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        return ChatSession.objects.filter(is_temp=True)


    @action(methods=["GET"], detail=False, url_path="current")
    def get_temp_session_detail(self, request):
        temp_session_id = request.GET.get('temp_session_id')
        if not temp_session_id:
            return Response({'detail': 'No temp_session_id provided'}, status=HTTP_400_BAD_REQUEST)
        session_obj = ChatSession.objects.filter(session_id=temp_session_id).first()
        if not session_obj:
            return Response({'detail': 'No active session object present'}, status=HTTP_400_BAD_REQUEST)
        response = ChatSessionDetailSerializer(session_obj).data

        return Response(response, status=HTTP_200_OK)


    @action(methods=["POST"], detail=False, url_path="send-message")
    def send_message(self, request, pk=None):
        data = request.data
        session_id = data.get('session_id')
        user_query = data.get('user_query')
        if session_id:
            session_obj = ChatSession.objects.filter(session_id=session_id).first()
        else:
            session_obj = None
        if not session_obj:
            session_obj = ChatSession.objects.create(
                name='Untitled'
            )

        user_message = ChatMessage.objects.create(
            session=session_obj,
            role='user',
            content=user_query
        )

        rag_agent = QdrantRAGAgent()
        response = rag_agent.get_response_for_new_user(user_message.content, str(session_obj.session_id))

        assistant_message = ChatMessage.objects.create(
            session=session_obj,
            role='assistant',
            content=response
        )

        session_obj.refresh_from_db()

        response = ChatSessionDetailSerializer(session_obj).data

        return Response(response, status=HTTP_200_OK)


class TaskAPI(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter()


class TutorAPI(APIView):

    def get(self, request, *args, **kwargs):
        user_query = request.GET.get('user_query')
        user_details = request.GET.get('user_details')
        user_level = request.GET.get('user_level')
        if not user_query:
            return Response({'detail': 'No user query provided'}, status=HTTP_400_BAD_REQUEST)

        try:
            rag_agent = QdrantRAGAgent(collection_name="tutorKB")
            response = rag_agent.get_response_for_tutor(
                user_query,
                user_details=user_details,
                user_level=user_level
            )
        except Exception as e:
            return Response({'detail': str(e)}, status=HTTP_400_BAD_REQUEST)

        return Response(response, status=HTTP_200_OK)