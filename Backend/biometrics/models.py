"""
COMITIA Biometrics Models
Basic models for biometric authentication (to be expanded)
"""

from django.db import models

# Placeholder model - will be expanded later
class BiometricTemplate(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'biometric_templates'
