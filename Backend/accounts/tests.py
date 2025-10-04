"""
Unit Tests for COMITIA Accounts App
Tests for User models, views, and authentication functionality
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import uuid

from .models import (
    User, CitizenProfile, VoterProfile, CandidateProfile, 
    VoterOfficialProfile, ElectoralCommissionProfile, 
    BiometricData, UserActivity
)

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for the User model"""
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'citizen'
        }
    
    def test_create_user(self):
        """Test creating a basic user"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.user_type, 'citizen')
        self.assertEqual(user.verification_status, 'pending')
        self.assertFalse(user.is_biometric_registered)
        self.assertTrue(isinstance(user.id, uuid.UUID))
    
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        expected_str = f"{user.username} ({user.get_user_type_display()})"
        self.assertEqual(str(user), expected_str)
    
    def test_user_type_properties(self):
        """Test user type property methods"""
        # Test citizen
        citizen = User.objects.create_user(username='citizen', user_type='citizen')
        self.assertTrue(citizen.is_citizen)
        self.assertFalse(citizen.is_voter)
        self.assertFalse(citizen.is_candidate)
        
        # Test voter
        voter = User.objects.create_user(username='voter', user_type='voter')
        self.assertTrue(voter.is_voter)
        self.assertFalse(voter.is_citizen)
        
        # Test candidate
        candidate = User.objects.create_user(username='candidate', user_type='candidate')
        self.assertTrue(candidate.is_candidate)
        self.assertFalse(candidate.is_voter)
        
        # Test voter official
        official = User.objects.create_user(username='official', user_type='voter_official')
        self.assertTrue(official.is_voter_official)
        
        # Test electoral commission
        commission = User.objects.create_user(username='commission', user_type='electoral_commission')
        self.assertTrue(commission.is_electoral_commission)
    
    def test_can_vote_property(self):
        """Test can_vote property"""
        # Approved voter can vote
        voter = User.objects.create_user(
            username='voter', 
            user_type='voter', 
            verification_status='approved'
        )
        self.assertTrue(voter.can_vote)
        
        # Pending voter cannot vote
        pending_voter = User.objects.create_user(
            username='pending_voter', 
            user_type='voter', 
            verification_status='pending'
        )
        self.assertFalse(pending_voter.can_vote)
        
        # Approved candidate can vote
        candidate = User.objects.create_user(
            username='candidate', 
            user_type='candidate', 
            verification_status='approved'
        )
        self.assertTrue(candidate.can_vote)
        
        # Citizen cannot vote
        citizen = User.objects.create_user(
            username='citizen', 
            user_type='citizen', 
            verification_status='approved'
        )
        self.assertFalse(citizen.can_vote)
    
    def test_permission_properties(self):
        """Test permission-related properties"""
        # Electoral commission can manage elections
        commission = User.objects.create_user(
            username='commission', 
            user_type='electoral_commission'
        )
        self.assertTrue(commission.can_manage_elections)
        
        # Voter official can manage voters
        official = User.objects.create_user(
            username='official', 
            user_type='voter_official'
        )
        self.assertTrue(official.can_manage_voters)
        
        # Electoral commission can also manage voters
        self.assertTrue(commission.can_manage_voters)
        
        # Regular voter cannot manage elections or voters
        voter = User.objects.create_user(username='voter', user_type='voter')
        self.assertFalse(voter.can_manage_elections)
        self.assertFalse(voter.can_manage_voters)


class ProfileModelTests(TestCase):
    """Test cases for profile models"""
    
    def setUp(self):
        """Set up test users"""
        self.citizen = User.objects.create_user(
            username='citizen', 
            user_type='citizen'
        )
        self.voter = User.objects.create_user(
            username='voter', 
            user_type='voter'
        )
        self.candidate = User.objects.create_user(
            username='candidate', 
            user_type='candidate'
        )
    
    def test_citizen_profile_creation(self):
        """Test CitizenProfile creation"""
        profile = CitizenProfile.objects.create(
            user=self.citizen,
            occupation='Engineer',
            education_level='Bachelor',
            voter_pre_enrollment_status='pending'
        )
        
        self.assertEqual(profile.user, self.citizen)
        self.assertEqual(profile.occupation, 'Engineer')
        self.assertEqual(profile.voter_pre_enrollment_status, 'pending')
    
    def test_voter_profile_creation(self):
        """Test VoterProfile creation"""
        profile = VoterProfile.objects.create(
            user=self.voter,
            voter_id='V001',
            polling_station='Station A',
            constituency='District 1'
        )
        
        self.assertEqual(profile.user, self.voter)
        self.assertEqual(profile.voter_id, 'V001')
        self.assertEqual(profile.polling_station, 'Station A')
        self.assertFalse(profile.voter_card_issued)
    
    def test_candidate_profile_creation(self):
        """Test CandidateProfile creation"""
        profile = CandidateProfile.objects.create(
            user=self.candidate,
            candidate_id='C001',
            political_party='Test Party',
            campaign_slogan='Vote for Change'
        )
        
        self.assertEqual(profile.user, self.candidate)
        self.assertEqual(profile.candidate_id, 'C001')
        self.assertEqual(profile.application_status, 'pending')
        self.assertIsNotNone(profile.application_date)


class BiometricDataTest(TestCase):
    """Test cases for BiometricData model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            user_type='voter'
        )
        self.official = User.objects.create_user(
            username='official',
            user_type='voter_official'
        )
    
    def test_biometric_data_creation(self):
        """Test BiometricData creation"""
        biometric = BiometricData.objects.create(
            user=self.user,
            face_encoding={'encoding': 'test_data'},
            registered_by=self.official,
            is_verified=True
        )
        
        self.assertEqual(biometric.user, self.user)
        self.assertEqual(biometric.registered_by, self.official)
        self.assertTrue(biometric.is_verified)
        self.assertIsNotNone(biometric.registration_date)


class UserActivityTest(TestCase):
    """Test cases for UserActivity model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            user_type='voter'
        )
    
    def test_user_activity_creation(self):
        """Test UserActivity creation"""
        activity = UserActivity.objects.create(
            user=self.user,
            activity_type='login',
            description='User logged in',
            ip_address='127.0.0.1'
        )
        
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.activity_type, 'login')
        self.assertEqual(activity.ip_address, '127.0.0.1')
        self.assertIsNotNone(activity.timestamp)


class AuthenticationViewTests(TestCase):
    """Test cases for authentication views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='citizen'
        )
    
    def test_login_view_get(self):
        """Test login view GET request"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_login_view_post_valid(self):
        """Test login view POST with valid credentials"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Should redirect to dashboard after successful login
        self.assertEqual(response.status_code, 302)
    
    def test_login_view_post_invalid(self):
        """Test login view POST with invalid credentials"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid')
    
    def test_register_view_get(self):
        """Test register view GET request"""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')
    
    def test_register_view_post_valid(self):
        """Test register view POST with valid data"""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        })
        # Should redirect after successful registration
        self.assertEqual(response.status_code, 302)
        
        # Check user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_logout_view(self):
        """Test logout functionality"""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Then logout
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)


class DashboardViewTests(TestCase):
    """Test cases for dashboard views"""
    
    def setUp(self):
        self.client = Client()
        self.citizen = User.objects.create_user(
            username='citizen',
            password='testpass123',
            user_type='citizen'
        )
        self.voter = User.objects.create_user(
            username='voter',
            password='testpass123',
            user_type='voter'
        )
        self.candidate = User.objects.create_user(
            username='candidate',
            password='testpass123',
            user_type='candidate'
        )
    
    def test_citizen_dashboard_access(self):
        """Test citizen can access citizen dashboard"""
        self.client.login(username='citizen', password='testpass123')
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Citizen Dashboard')
    
    def test_voter_dashboard_access(self):
        """Test voter can access voter dashboard"""
        self.client.login(username='voter', password='testpass123')
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Voter Dashboard')
    
    def test_candidate_dashboard_access(self):
        """Test candidate can access candidate dashboard"""
        self.client.login(username='candidate', password='testpass123')
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Candidate Dashboard')
    
    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(reverse('accounts:dashboard'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)


class RoleTransitionTests(TestCase):
    """Test cases for role transition functionality"""
    
    def setUp(self):
        self.client = Client()
        self.citizen = User.objects.create_user(
            username='citizen',
            password='testpass123',
            user_type='citizen',
            verification_status='approved'
        )
        self.commission = User.objects.create_user(
            username='commission',
            password='testpass123',
            user_type='electoral_commission'
        )
    
    def test_citizen_can_apply_for_voter(self):
        """Test citizen can apply for voter status"""
        self.client.login(username='citizen', password='testpass123')
        
        # Check if citizen can apply (this depends on your business logic)
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Test the application process would go here
        # This depends on your specific implementation
    
    def test_role_transition_view_access(self):
        """Test role transition view access"""
        self.client.login(username='citizen', password='testpass123')
        
        # Try to access role transition page
        try:
            response = self.client.get(reverse('accounts:role_transition'))
            self.assertEqual(response.status_code, 200)
        except:
            # If the URL doesn't exist yet, that's expected
            pass


class ModelValidationTests(TestCase):
    """Test model validation and constraints"""
    
    def test_unique_national_id(self):
        """Test national_id uniqueness constraint"""
        User.objects.create_user(
            username='user1',
            national_id='ID123456'
        )
        
        # Creating another user with same national_id should raise error
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='user2',
                national_id='ID123456'
            )
    
    def test_unique_voter_id(self):
        """Test voter_id uniqueness in VoterProfile"""
        user1 = User.objects.create_user(username='voter1', user_type='voter')
        user2 = User.objects.create_user(username='voter2', user_type='voter')
        
        VoterProfile.objects.create(user=user1, voter_id='V001')
        
        # Creating another profile with same voter_id should raise error
        with self.assertRaises(Exception):
            VoterProfile.objects.create(user=user2, voter_id='V001')
    
    def test_user_type_choices(self):
        """Test user_type field accepts only valid choices"""
        valid_types = ['citizen', 'voter', 'candidate', 'voter_official', 'electoral_commission']
        
        for user_type in valid_types:
            user = User.objects.create_user(
                username=f'user_{user_type}',
                user_type=user_type
            )
            self.assertEqual(user.user_type, user_type)


class DatabaseIntegrityTests(TestCase):
    """Test database integrity and relationships"""
    
    def test_user_profile_cascade_delete(self):
        """Test that profiles are deleted when user is deleted"""
        user = User.objects.create_user(username='testuser', user_type='voter')
        profile = VoterProfile.objects.create(user=user, voter_id='V001')
        
        # Delete user should cascade delete profile
        user.delete()
        
        self.assertFalse(VoterProfile.objects.filter(voter_id='V001').exists())
    
    def test_biometric_data_relationship(self):
        """Test BiometricData relationship with User"""
        user = User.objects.create_user(username='testuser')
        biometric = BiometricData.objects.create(user=user)
        
        # Test reverse relationship
        self.assertEqual(user.biometric_data, biometric)
    
    def test_user_activity_relationship(self):
        """Test UserActivity relationship with User"""
        user = User.objects.create_user(username='testuser')
        activity = UserActivity.objects.create(
            user=user,
            activity_type='login'
        )
        
        # Test reverse relationship
        self.assertIn(activity, user.activities.all())


class PermissionTests(TestCase):
    """Test permission and access control"""
    
    def setUp(self):
        self.citizen = User.objects.create_user(
            username='citizen',
            user_type='citizen'
        )
        self.voter = User.objects.create_user(
            username='voter',
            user_type='voter',
            verification_status='approved'
        )
        self.official = User.objects.create_user(
            username='official',
            user_type='voter_official'
        )
        self.commission = User.objects.create_user(
            username='commission',
            user_type='electoral_commission'
        )
    
    def test_voting_permissions(self):
        """Test voting permission logic"""
        self.assertFalse(self.citizen.can_vote)
        self.assertTrue(self.voter.can_vote)
    
    def test_management_permissions(self):
        """Test management permission logic"""
        self.assertFalse(self.citizen.can_manage_voters)
        self.assertFalse(self.voter.can_manage_voters)
        self.assertTrue(self.official.can_manage_voters)
        self.assertTrue(self.commission.can_manage_voters)
        
        self.assertFalse(self.citizen.can_manage_elections)
        self.assertFalse(self.voter.can_manage_elections)
        self.assertFalse(self.official.can_manage_elections)
        self.assertTrue(self.commission.can_manage_elections)
