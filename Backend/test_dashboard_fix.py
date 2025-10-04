#!/usr/bin/env python
"""
Test script to verify dashboard fixes
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comitia.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import VoterProfile, CandidateProfile, VoterOfficialProfile, ElectoralCommissionProfile

User = get_user_model()

def test_dashboard_fixes():
    print("🧪 Testing Dashboard Profile Creation Fixes")
    print("=" * 50)
    
    # Create a test user
    try:
        test_user = User.objects.create_user(
            username='testdashboard',
            email='test@dashboard.com',
            password='testpass123'
        )
        print("✅ Test user created")
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return
    
    # Test VoterProfile creation
    try:
        import uuid
        voter_id = f"VTR{str(uuid.uuid4())[:8].upper()}"
        voter_profile, created = VoterProfile.objects.get_or_create(
            user=test_user,
            defaults={'voter_id': voter_id}
        )
        print(f"✅ VoterProfile created with ID: {voter_profile.voter_id}")
    except Exception as e:
        print(f"❌ VoterProfile creation failed: {e}")
    
    # Test CandidateProfile creation
    try:
        candidate_id = f"CND{str(uuid.uuid4())[:8].upper()}"
        candidate_profile, created = CandidateProfile.objects.get_or_create(
            user=test_user,
            defaults={'candidate_id': candidate_id}
        )
        print(f"✅ CandidateProfile created with ID: {candidate_profile.candidate_id}")
    except Exception as e:
        print(f"❌ CandidateProfile creation failed: {e}")
    
    # Test VoterOfficialProfile creation
    try:
        official_id = f"OFF{str(uuid.uuid4())[:8].upper()}"
        official_profile, created = VoterOfficialProfile.objects.get_or_create(
            user=test_user,
            defaults={'official_id': official_id}
        )
        print(f"✅ VoterOfficialProfile created with ID: {official_profile.official_id}")
    except Exception as e:
        print(f"❌ VoterOfficialProfile creation failed: {e}")
    
    # Test ElectoralCommissionProfile creation
    try:
        commission_id = f"COM{str(uuid.uuid4())[:8].upper()}"
        commission_profile, created = ElectoralCommissionProfile.objects.get_or_create(
            user=test_user,
            defaults={'commission_id': commission_id}
        )
        print(f"✅ ElectoralCommissionProfile created with ID: {commission_profile.commission_id}")
    except Exception as e:
        print(f"❌ ElectoralCommissionProfile creation failed: {e}")
    
    # Clean up
    try:
        test_user.delete()
        print("✅ Test user and profiles cleaned up")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
    
    print("\n🎯 Dashboard fix test completed!")
    print("The UNIQUE constraint errors should now be resolved.")

if __name__ == '__main__':
    test_dashboard_fixes()
