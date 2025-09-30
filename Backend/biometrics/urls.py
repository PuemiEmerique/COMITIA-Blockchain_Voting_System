"""
COMITIA Biometrics URLs
Biometric authentication endpoints
"""

from django.urls import path
from . import views

urlpatterns = [
    # Biometric Registration
    path('register/', views.register_biometric, name='register-biometric'),
    path('verify/', views.verify_biometric, name='verify-biometric'),
    
    # Face Recognition
    path('face/capture/', views.capture_face, name='capture-face'),
    path('face/verify/', views.verify_face, name='verify-face'),
    
    # Biometric Status
    path('status/', views.get_biometric_status, name='get-biometric-status'),
]
