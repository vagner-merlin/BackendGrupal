"""
URLs para el Asistente de IA
"""
from django.urls import path, include
from rest_framework import routers
from .api_assistant import AssistantViewSet

router = routers.DefaultRouter()
router.register(r'assistant', AssistantViewSet, basename='assistant')

urlpatterns = [
    path('', include(router.urls)),
]
