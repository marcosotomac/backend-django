"""
URLs para el sistema de Stories
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StoryViewSet, StoryHighlightViewSet

router = DefaultRouter()
router.register(r'stories', StoryViewSet, basename='story')
router.register(r'highlights', StoryHighlightViewSet,
                basename='storyhighlight')

urlpatterns = [
    path('', include(router.urls)),
]
