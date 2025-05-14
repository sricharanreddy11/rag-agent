from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from core.services.qdrant_service import QdrantRAGAgent
from university_agent.models import ChatSession, ChatMessage
from university_agent.serializers import ChatSessionDetailSerializer, \
    ChatSessionListSerializer


class ChatSessionAPI(viewsets.ModelViewSet):
    serializer_class = ChatSessionListSerializer
    permission_classes = []
    authentication_classes = []

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChatSessionDetailSerializer
        return ChatSessionListSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ChatSession.objects.filter(user=self.request.user)
        temp_session_id = self.request.query_params.get('temp_session_id')
        if not temp_session_id:
            return ChatSession.objects.none()
        return ChatSession.objects.filter(session_id=temp_session_id)


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
        response = rag_agent.get_response(user_message.content, str(session_obj.session_id))

        assistant_message = ChatMessage.objects.create(
            session=session_obj,
            role='assistant',
            content=response
        )

        session_obj.refresh_from_db()

        response = ChatSessionDetailSerializer(session_obj).data

        return Response(response, status=HTTP_200_OK)
