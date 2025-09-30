"""
COMITIA Biometrics Views
Basic biometric endpoints (to be expanded)
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_biometric(request):
    return Response({'message': 'Register biometric endpoint - to be implemented'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_biometric(request):
    return Response({'message': 'Verify biometric endpoint - to be implemented'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def capture_face(request):
    return Response({'message': 'Capture face endpoint - to be implemented'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_face(request):
    return Response({'message': 'Verify face endpoint - to be implemented'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_biometric_status(request):
    return Response({'message': 'Biometric status endpoint - to be implemented'})
