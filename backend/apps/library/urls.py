from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, CheckoutViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'checkouts', CheckoutViewSet, basename='checkout')

urlpatterns = [
    path('', include(router.urls)),
]
