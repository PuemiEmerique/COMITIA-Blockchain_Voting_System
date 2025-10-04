#!/usr/bin/env python
"""
Individual Functionality Tests for COMITIA
Each test is separate and can be run independently
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comitia.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


def test_1_login():
    """1. TESTING LOGIN"""
    print("\n1️⃣  TESTING LOGIN FUNCTIONALITY")
    print("=" * 40)
    
    try:
        # Create test user
        user = User.objects.create_user(
            username='logintest',
            password='testpass123',
            email='login@test.com'
        )
        print("✅ Test user created")
        
        # Test login
        client = Client()
        response = client.post('/accounts/login/', {
            'username': 'logintest',
            'password': 'testpass123'
        })
        
        if response.status_code == 302:  # Redirect means success
            print("✅ LOGIN WORKING - User can login successfully")
            print(f"   - Username: logintest")
            print(f"   - Response: Redirected to dashboard")
        else:
            print("❌ LOGIN ISSUE - Check login implementation")
            print(f"   - Status Code: {response.status_code}")
        
        # Test invalid login
        response = client.post('/accounts/login/', {
            'username': 'logintest',
            'password': 'wrongpass'
        })
        
        if response.status_code == 200:  # Stays on page means failed login
            print("✅ SECURITY WORKING - Invalid credentials rejected")
        
        # Cleanup
        user.delete()
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print("-" * 40)


def test_2_registration():
    """2. TESTING REGISTRATION"""
    print("\n2️⃣  TESTING REGISTRATION FUNCTIONALITY")
    print("=" * 40)
    
    try:
        client = Client()
        
        # Test registration page loads
        response = client.get('/accounts/register/')
        if response.status_code == 200:
            print("✅ Registration page loads successfully")
        else:
            print("❌ Registration page not accessible")
            return
        
        # Test user registration
        registration_data = {
            'username': 'newuser123',
            'email': 'newuser@test.com',
            'password1': 'testpass123456',
            'password2': 'testpass123456',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/accounts/register/', registration_data)
        
        # Check if user was created
        if User.objects.filter(username='newuser123').exists():
            print("✅ REGISTRATION WORKING - New user created successfully")
            print(f"   - Username: newuser123")
            print(f"   - Email: newuser@test.com")
            
            # Cleanup
            User.objects.filter(username='newuser123').delete()
        else:
            print("❌ REGISTRATION ISSUE - User not created")
            print(f"   - Response Status: {response.status_code}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print("-" * 40)


def test_3_dashboard():
    """3. TESTING DASHBOARD ACCESS"""
    print("\n3️⃣  TESTING DASHBOARD ACCESS")
    print("=" * 40)
    
    try:
        # Create test users
        citizen = User.objects.create_user(
            username='citizen123',
            password='testpass123',
            user_type='citizen'
        )
        
        voter = User.objects.create_user(
            username='voter123',
            password='testpass123',
            user_type='voter'
        )
        
        client = Client()
        
        # Test unauthenticated access
        response = client.get('/accounts/dashboard/')
        if response.status_code == 302:  # Should redirect to login
            print("✅ SECURITY WORKING - Dashboard requires authentication")
        
        # Test citizen dashboard
        client.login(username='citizen123', password='testpass123')
        response = client.get('/accounts/dashboard/')
        if response.status_code == 200:
            print("✅ CITIZEN DASHBOARD WORKING")
            print(f"   - User Type: Citizen")
            print(f"   - Access: Granted")
        else:
            print("❌ CITIZEN DASHBOARD ISSUE")
            print(f"   - Status Code: {response.status_code}")
        
        # Test voter dashboard
        client.logout()
        client.login(username='voter123', password='testpass123')
        response = client.get('/accounts/dashboard/')
        if response.status_code == 200:
            print("✅ VOTER DASHBOARD WORKING")
            print(f"   - User Type: Voter")
            print(f"   - Access: Granted")
        else:
            print("❌ VOTER DASHBOARD ISSUE")
            print(f"   - Status Code: {response.status_code}")
        
        # Cleanup
        citizen.delete()
        voter.delete()
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print("-" * 40)


def test_4_user_creation():
    """4. TESTING USER MODEL"""
    print("\n4️⃣  TESTING USER MODEL")
    print("=" * 40)
    
    try:
        # Test basic user creation
        user = User.objects.create_user(
            username='modeltest',
            email='model@test.com',
            password='testpass123',
            first_name='Model',
            last_name='Test',
            user_type='citizen'
        )
        
        # Test user properties
        if user.username == 'modeltest':
            print("✅ USER CREATION WORKING")
            print(f"   - Username: {user.username}")
            print(f"   - Email: {user.email}")
            print(f"   - User Type: {user.user_type}")
            print(f"   - Full Name: {user.get_full_name()}")
        
        # Test user type properties
        if user.is_citizen:
            print("✅ USER TYPE PROPERTIES WORKING")
            print(f"   - Is Citizen: {user.is_citizen}")
            print(f"   - Is Voter: {user.is_voter}")
            print(f"   - Can Vote: {user.can_vote}")
        
        # Test different user types
        voter = User.objects.create_user(
            username='votertest',
            user_type='voter',
            verification_status='approved'
        )
        
        if voter.is_voter and voter.can_vote:
            print("✅ VOTER TYPE WORKING")
            print(f"   - Is Voter: {voter.is_voter}")
            print(f"   - Can Vote: {voter.can_vote}")
        
        # Cleanup
        user.delete()
        voter.delete()
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print("-" * 40)


def test_5_permissions():
    """5. TESTING USER PERMISSIONS"""
    print("\n5️⃣  TESTING USER PERMISSIONS")
    print("=" * 40)
    
    try:
        # Create users with different roles
        citizen = User.objects.create_user(username='citizen_perm', user_type='citizen')
        voter = User.objects.create_user(username='voter_perm', user_type='voter', verification_status='approved')
        official = User.objects.create_user(username='official_perm', user_type='voter_official')
        commission = User.objects.create_user(username='commission_perm', user_type='electoral_commission')
        
        # Test voting permissions
        voting_results = {
            'Citizen': citizen.can_vote,
            'Voter': voter.can_vote,
            'Official': official.can_vote,
            'Commission': commission.can_vote
        }
        
        print("✅ VOTING PERMISSIONS:")
        for role, can_vote in voting_results.items():
            print(f"   - {role} can vote: {can_vote}")
        
        # Test management permissions
        management_results = {
            'Official can manage voters': official.can_manage_voters,
            'Commission can manage voters': commission.can_manage_voters,
            'Commission can manage elections': commission.can_manage_elections,
            'Citizen can manage voters': citizen.can_manage_voters
        }
        
        print("✅ MANAGEMENT PERMISSIONS:")
        for permission, has_permission in management_results.items():
            print(f"   - {permission}: {has_permission}")
        
        # Cleanup
        for user in [citizen, voter, official, commission]:
            user.delete()
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print("-" * 40)


def test_6_logout():
    """6. TESTING LOGOUT"""
    print("\n6️⃣  TESTING LOGOUT FUNCTIONALITY")
    print("=" * 40)
    
    try:
        # Create test user
        user = User.objects.create_user(
            username='logouttest',
            password='testpass123'
        )
        
        client = Client()
        
        # Login first
        login_success = client.login(username='logouttest', password='testpass123')
        if login_success:
            print("✅ User logged in successfully")
        
        # Test logout
        response = client.post('/accounts/logout/')
        if response.status_code == 302:  # Should redirect
            print("✅ LOGOUT WORKING - User logged out successfully")
            print(f"   - Response: Redirected after logout")
        
        # Verify logout by trying to access dashboard
        response = client.get('/accounts/dashboard/')
        if response.status_code == 302:  # Should redirect to login
            print("✅ LOGOUT VERIFIED - Dashboard requires re-authentication")
        
        # Cleanup
        user.delete()
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print("-" * 40)


def run_all_individual_tests():
    """Run all individual tests"""
    print("🧪 COMITIA INDIVIDUAL FUNCTIONALITY TESTS")
    print("=" * 60)
    print("Testing each functionality separately...")
    
    # Run each test
    test_1_login()
    test_2_registration()
    test_3_dashboard()
    test_4_user_creation()
    test_5_permissions()
    test_6_logout()
    
    print("\n🎯 TESTING COMPLETE!")
    print("=" * 60)
    print("Each functionality has been tested individually.")
    print("Check the results above for any issues.")


if __name__ == '__main__':
    run_all_individual_tests()
