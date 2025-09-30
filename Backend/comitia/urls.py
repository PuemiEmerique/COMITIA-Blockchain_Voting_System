"""
COMITIA URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

# API Documentation (drf_yasg temporarily disabled)
# from rest_framework import permissions
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi
# schema_view = get_schema_view(...)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Main Web Views
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('help/', views.help_center, name='help_center'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_of_service, name='terms_of_service'),
    path('status/', views.system_status, name='system_status'),
    path('security/', views.security_report, name='security_report'),
    
    # App URLs
    path('accounts/', include('accounts.urls')),
    # path('elections/', include('elections.urls')),
    # path('voting/', include('voting.urls')),
    # path('blockchain/', include('blockchain.urls')),
    # path('biometrics/', include('biometrics.urls')),
    # path('campaigns/', include('campaigns.urls')),
    
    # API Documentation (temporarily disabled)
    path('api/docs/', views.api_documentation, name='api_documentation'),
    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API Endpoints (temporarily disabled until apps are created)
    # path('api/v1/auth/', include('accounts.api_urls')),
    # path('api/v1/elections/', include('elections.api_urls')),
    # path('api/v1/voting/', include('voting.api_urls')),
    # path('api/v1/blockchain/', include('blockchain.api_urls')),
    # path('api/v1/biometrics/', include('biometrics.api_urls')),
    # path('api/v1/campaigns/', include('campaigns.api_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
