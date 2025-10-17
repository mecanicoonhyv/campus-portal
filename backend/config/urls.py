from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Authentication
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # App URLs
    path('api/users/', include('apps.users.urls')),
    path('api/academics/', include('apps.academics.urls')),
    path('api/assessments/', include('apps.assessments.urls')),
    path('api/attendance/', include('apps.attendance.urls')),
    path('api/library/', include('apps.library.urls')),
    path('api/services/', include('apps.services.urls')),
    path('api/facilities/', include('apps.facilities.urls')),
]
