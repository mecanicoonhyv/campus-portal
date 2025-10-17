from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinancialAidViewSet, ParkingPermitViewSet, EventViewSet

router = DefaultRouter()
router.register(r'financial-aid', FinancialAidViewSet, basename='financial-aid')
router.register(r'parking', ParkingPermitViewSet, basename='parking')
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
]
