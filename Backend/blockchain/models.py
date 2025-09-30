"""
COMITIA Blockchain Models
Basic models for blockchain integration (to be expanded)
"""

from django.db import models

# Placeholder model - will be expanded later
class SmartContract(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=42)
    network = models.CharField(max_length=50)
    deployed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'smart_contracts'
