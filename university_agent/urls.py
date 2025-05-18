from django.urls import path, include
from rest_framework.routers import DefaultRouter
from university_agent.views import ChatSessionAPI, TempSessionAPI, TaskAPI, TutorAPI

router = DefaultRouter()
router.register(r'chat/sessions', ChatSessionAPI, basename='ChatSessionAPI')
router.register(r'chat/temp-session', TempSessionAPI, basename='TempSessionAPI')
router.register(r'tasks', TaskAPI, basename='TaskAPI')

urlpatterns = [
    path('', include(router.urls)),
    path('tutor/', TutorAPI.as_view(), name='tutor-api'),
]