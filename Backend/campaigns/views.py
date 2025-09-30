"""
COMITIA Campaigns Views
Basic campaign endpoints (to be expanded)
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_campaigns(request):
    return Response({'message': 'My campaigns endpoint - to be implemented'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_campaign(request):
    return Response({'message': 'Create campaign endpoint - to be implemented'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_campaign_detail(request, campaign_id):
    return Response({'message': 'Campaign detail endpoint - to be implemented'})

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_campaign(request, campaign_id):
    return Response({'message': 'Update campaign endpoint - to be implemented'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_campaign_media(request, campaign_id):
    return Response({'message': 'Upload campaign media endpoint - to be implemented'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_campaign_posts(request, campaign_id):
    return Response({'message': 'Campaign posts endpoint - to be implemented'})

@api_view(['GET'])
def get_public_campaigns(request):
    return Response({'message': 'Public campaigns endpoint - to be implemented'})

@api_view(['GET'])
def get_public_campaign_detail(request, campaign_id):
    return Response({'message': 'Public campaign detail endpoint - to be implemented'})
