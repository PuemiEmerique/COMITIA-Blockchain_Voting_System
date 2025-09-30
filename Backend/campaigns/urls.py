"""
COMITIA Campaigns URLs
Campaign management endpoints
"""

from django.urls import path
from . import views

urlpatterns = [
    # Campaign Management
    path('my-campaigns/', views.get_my_campaigns, name='get-my-campaigns'),
    path('create/', views.create_campaign, name='create-campaign'),
    path('<uuid:campaign_id>/', views.get_campaign_detail, name='get-campaign-detail'),
    path('<uuid:campaign_id>/update/', views.update_campaign, name='update-campaign'),
    
    # Campaign Content
    path('<uuid:campaign_id>/upload-media/', views.upload_campaign_media, name='upload-campaign-media'),
    path('<uuid:campaign_id>/posts/', views.get_campaign_posts, name='get-campaign-posts'),
    
    # Public Campaign Views
    path('public/', views.get_public_campaigns, name='get-public-campaigns'),
    path('public/<uuid:campaign_id>/', views.get_public_campaign_detail, name='get-public-campaign-detail'),
]
