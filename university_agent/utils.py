from university_agent.models import ChatSession
from university_agent.serializers import ChatSessionDetailSerializer


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