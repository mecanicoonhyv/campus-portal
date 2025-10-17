from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BuildingViewSet, RoomViewSet

router = DefaultRouter()
router.register(r'buildings', BuildingViewSet, basename='building')
router.register(r'rooms', RoomViewSet, basename='room')

urlpatterns = [
    path('', include(router.urls)),
]
