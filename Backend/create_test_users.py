#!/usr/bin/env python
"""
Script to create test users with different roles for COMITIA
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comitia.settings')
django.setup()

from accounts.models import User, CitizenProfile, VoterProfile, CandidateProfile, VoterOfficialProfile, ElectoralCommissionProfile

def create_test_users():
    """Create test users with different roles"""
    users_data = [
        {
            'username': 'voter_user', 
            'email': 'voter@test.com', 
            'password': 'test123', 
            'user_type': 'voter', 
            'first_name': 'John', 
            'last_name': 'Voter'
        },
        {
            'username': 'candidate_user', 
            'email': 'candidate@test.com', 
            'password': 'test123', 
            'user_type': 'candidate', 
            'first_name': 'Jane', 
            'last_name': 'Candidate'
        },
        {
            'username': 'official_user', 
            'email': 'official@test.com', 
            'password': 'test123', 
            'user_type': 'voter_official', 
            'first_name': 'Bob', 
            'last_name': 'Official'
        },
        {
            'username': 'commission_user', 
            'email': 'commission@test.com', 
            'password': 'test123', 
            'user_type': 'electoral_commission', 
            'first_name': 'Alice', 
            'last_name': 'Commission'
        }
    ]

    for user_data in users_data:
        try:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    user_type=user_data['user_type']
                )
                
                # Create appropriate profiles
                if user_data['user_type'] == 'voter':
                    VoterProfile.objects.create(user=user)
                elif user_data['user_type'] == 'candidate':
                    CandidateProfile.objects.create(user=user)
                elif user_data['user_type'] == 'voter_official':
                    VoterOfficialProfile.objects.create(user=user)
                elif user_data['user_type'] == 'electoral_commission':
                    ElectoralCommissionProfile.objects.create(user=user)
                
                print(f'✅ Created {user_data["user_type"]} user: {user_data["username"]}')
            else:
                print(f'⚠️  User {user_data["username"]} already exists')
        except Exception as e:
            print(f'❌ Error creating user {user_data["username"]}: {e}')

    print('\n🎉 Test users creation completed!')
    print('\n📋 Available test accounts:')
    print('- voter_user / test123 (Voter Dashboard)')
    print('- candidate_user / test123 (Candidate Dashboard)')  
    print('- official_user / test123 (Voter Official Dashboard)')
    print('- commission_user / test123 (Electoral Commission Dashboard)')

if __name__ == '__main__':
    create_test_users()
