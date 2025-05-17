from django.urls import path, include
from rest_framework.routers import DefaultRouter
from university_agent.views import ChatSessionAPI, TempSessionAPI

router = DefaultRouter()
router.register(r'chat/sessions', ChatSessionAPI, basename='ChatSessionAPI')
router.register(r'chat/temp-session', TempSessionAPI, basename='TempSessionAPI')

urlpatterns = [
    path('', include(router.urls)),
]