"""
COMITIA Simple Comprehensive Unit Tests
Each test covers one specific functionality with clear reporting
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comitia.settings')
django.setup()

User = get_user_model()


class SimpleTestSuite(TestCase):
    """Simple comprehensive test suite for COMITIA"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        print("\n" + "="*60)
        print("🧪 COMITIA SIMPLE TEST SUITE")
        print("="*60)
    
    # ========================================
    # 1. TESTING USER MODEL
    # ========================================
    
    def test_1_user_creation(self):
        """1. Testing User Creation"""
        print("\n1️⃣  TESTING USER CREATION")
        print("-" * 30)
        
        # Create a user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='citizen'
        )
        
        # Test user properties
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.user_type, 'citizen')
        self.assertEqual(user.verification_status, 'pending')
        self.assertTrue(user.is_citizen)
        self.assertFalse(user.is_voter)
        
        print("✅ User created successfully")
        print(f"   - Username: {user.username}")
        print(f"   - Email: {user.email}")
        print(f"   - User Type: {user.user_type}")
        print(f"   - Status: {user.verification_status}")
        print("✅ User properties working correctly")
    
    # ========================================
    # 2. TESTING USER REGISTRATION
    # ========================================
    
    def test_2_user_registration(self):
        """2. Testing User Registration"""
        print("\n2️⃣  TESTING USER REGISTRATION")
        print("-" * 30)
        
        # Test GET request to registration page
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)
        print("✅ Registration page loads successfully")
        
        # Test POST request with valid data
        registration_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123456',
            'password2': 'newpass123456',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post('/accounts/register/', registration_data)
        
        # Check if user was created
        user_exists = User.objects.filter(username='newuser').exists()
        self.assertTrue(user_exists)
        
        print("✅ User registration successful")
        print(f"   - New user created: newuser")
        print(f"   - Email: newuser@example.com")
        print(f"   - Response status: {response.status_code}")
    
    # ========================================
    # 3. TESTING LOGIN FUNCTIONALITY
    # ========================================
    
    def test_3_login_functionality(self):
        """3. Testing Login Functionality"""
        print("\n3️⃣  TESTING LOGIN FUNCTIONALITY")
        print("-" * 30)
        
        # Create a test user
        user = User.objects.create_user(
            username='loginuser',
            email='login@example.com',
            password='loginpass123',
            user_type='citizen'
        )
        
        # Test GET request to login page
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        print("✅ Login page loads successfully")
        
        # Test POST request with valid credentials
        login_data = {
            'username': 'loginuser',
            'password': 'loginpass123'
        }
        
        response = self.client.post('/accounts/login/', login_data)
        
        # Check if login was successful (should redirect)
        self.assertEqual(response.status_code, 302)
        print("✅ Login successful with valid credentials")
        print(f"   - Username: loginuser")
        print(f"   - Redirected to: {response.url if hasattr(response, 'url') else 'dashboard'}")
        
        # Test invalid credentials
        invalid_data = {
            'username': 'loginuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/accounts/login/', invalid_data)
        self.assertEqual(response.status_code, 200)  # Should stay on login page
        print("✅ Login correctly rejects invalid credentials")
    
    # ========================================
    # 4. TESTING DASHBOARD ACCESS
    # ========================================
    
    def test_4_dashboard_access(self):
        """4. Testing Dashboard Access"""
        print("\n4️⃣  TESTING DASHBOARD ACCESS")
        print("-" * 30)
        
        # Create users with different roles
        citizen = User.objects.create_user(
            username='citizen_user',
            password='testpass123',
            user_type='citizen'
        )
        
        voter = User.objects.create_user(
            username='voter_user',
            password='testpass123',
            user_type='voter'
        )
        
        # Test unauthenticated access (should redirect to login)
        response = self.client.get('/accounts/dashboard/')
        self.assertEqual(response.status_code, 302)
        print("✅ Dashboard correctly requires authentication")
        
        # Test citizen dashboard access
        self.client.login(username='citizen_user', password='testpass123')
        response = self.client.get('/accounts/dashboard/')
        self.assertEqual(response.status_code, 200)
        print("✅ Citizen can access dashboard")
        print(f"   - Response status: {response.status_code}")
        
        # Logout and test voter dashboard
        self.client.logout()
        self.client.login(username='voter_user', password='testpass123')
        response = self.client.get('/accounts/dashboard/')
        self.assertEqual(response.status_code, 200)
        print("✅ Voter can access dashboard")
        print(f"   - Response status: {response.status_code}")
    
    # ========================================
    # 5. TESTING USER PERMISSIONS
    # ========================================
    
    def test_5_user_permissions(self):
        """5. Testing User Permissions"""
        print("\n5️⃣  TESTING USER PERMISSIONS")
        print("-" * 30)
        
        # Create users with different roles
        citizen = User.objects.create_user(
            username='perm_citizen',
            user_type='citizen',
            verification_status='approved'
        )
        
        voter = User.objects.create_user(
            username='perm_voter',
            user_type='voter',
            verification_status='approved'
        )
        
        candidate = User.objects.create_user(
            username='perm_candidate',
            user_type='candidate',
            verification_status='approved'
        )
        
        official = User.objects.create_user(
            username='perm_official',
            user_type='voter_official'
        )
        
        commission = User.objects.create_user(
            username='perm_commission',
            user_type='electoral_commission'
        )
        
        # Test voting permissions
        self.assertFalse(citizen.can_vote)
        self.assertTrue(voter.can_vote)
        self.assertTrue(candidate.can_vote)
        print("✅ Voting permissions working correctly")
        print(f"   - Citizen can vote: {citizen.can_vote}")
        print(f"   - Voter can vote: {voter.can_vote}")
        print(f"   - Candidate can vote: {candidate.can_vote}")
        
        # Test management permissions
        self.assertFalse(citizen.can_manage_voters)
        self.assertTrue(official.can_manage_voters)
        self.assertTrue(commission.can_manage_voters)
        self.assertTrue(commission.can_manage_elections)
        print("✅ Management permissions working correctly")
        print(f"   - Official can manage voters: {official.can_manage_voters}")
        print(f"   - Commission can manage elections: {commission.can_manage_elections}")
    
    # ========================================
    # 6. TESTING USER TYPES
    # ========================================
    
    def test_6_user_types(self):
        """6. Testing User Types"""
        print("\n6️⃣  TESTING USER TYPES")
        print("-" * 30)
        
        # Test all user types
        user_types = [
            ('citizen', 'is_citizen'),
            ('voter', 'is_voter'),
            ('candidate', 'is_candidate'),
            ('voter_official', 'is_voter_official'),
            ('electoral_commission', 'is_electoral_commission')
        ]
        
        for user_type, property_name in user_types:
            user = User.objects.create_user(
                username=f'test_{user_type}',
                user_type=user_type
            )
            
            # Check that the correct property is True
            self.assertTrue(getattr(user, property_name))
            print(f"✅ {user_type.replace('_', ' ').title()} user type working")
            print(f"   - Username: {user.username}")
            print(f"   - Type: {user.get_user_type_display()}")
    
    # ========================================
    # 7. TESTING LOGOUT FUNCTIONALITY
    # ========================================
    
    def test_7_logout_functionality(self):
        """7. Testing Logout Functionality"""
        print("\n7️⃣  TESTING LOGOUT FUNCTIONALITY")
        print("-" * 30)
        
        # Create and login user
        user = User.objects.create_user(
            username='logoutuser',
            password='testpass123',
            user_type='citizen'
        )
        
        # Login first
        login_success = self.client.login(username='logoutuser', password='testpass123')
        self.assertTrue(login_success)
        print("✅ User logged in successfully")
        
        # Test logout
        response = self.client.post('/accounts/logout/')
        self.assertEqual(response.status_code, 302)  # Should redirect after logout
        print("✅ Logout successful")
        print(f"   - Response status: {response.status_code}")
        
        # Verify user is logged out by trying to access dashboard
        response = self.client.get('/accounts/dashboard/')
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        print("✅ User successfully logged out (dashboard requires re-authentication)")


def run_simple_tests():
    """Run the simple test suite"""
    import unittest
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleTestSuite)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ ERRORS:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {len(result.failures + result.errors)} TESTS FAILED")
    
    print("="*60)


if __name__ == '__main__':
    run_simple_tests()
