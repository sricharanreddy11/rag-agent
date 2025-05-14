from django.urls import path, include
from rest_framework.routers import DefaultRouter
from university_agent.views import ChatSessionAPI

router = DefaultRouter()
router.register(r'chat/sessions', ChatSessionAPI, basename='ChatSessionAPI')

urlpatterns = [
    path('', include(router.urls)),
]