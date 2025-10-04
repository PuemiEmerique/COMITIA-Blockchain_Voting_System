"""
Unit Tests for COMITIA Elections App
Tests for Election models and related functionality
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from .models import (
    Election, ElectionPosition, ElectionCandidate, ElectionConstituency,
    PollingStation, ElectionResult, ElectionAuditLog, ElectionNotification
)

User = get_user_model()


class ElectionModelTest(TestCase):
    """Test cases for the Election model"""
    
    def setUp(self):
        """Set up test data"""
        self.commission_user = User.objects.create_user(
            username='commission',
            user_type='electoral_commission'
        )
        
        self.election_data = {
            'title': 'Test Presidential Election 2024',
            'description': 'Test election for unit testing',
            'election_type': 'presidential',
            'registration_start_date': timezone.now() + timedelta(days=1),
            'registration_end_date': timezone.now() + timedelta(days=30),
            'voting_start_date': timezone.now() + timedelta(days=31),
            'voting_end_date': timezone.now() + timedelta(days=32),
            'created_by': self.commission_user
        }
    
    def test_create_election(self):
        """Test creating a basic election"""
        election = Election.objects.create(**self.election_data)
        
        self.assertEqual(election.title, 'Test Presidential Election 2024')
        self.assertEqual(election.election_type, 'presidential')
        self.assertEqual(election.status, 'draft')
        self.assertEqual(election.created_by, self.commission_user)
        self.assertTrue(isinstance(election.id, uuid.UUID))
        self.assertEqual(election.total_votes_cast, 0)
        self.assertFalse(election.results_published)
    
    def test_election_str_representation(self):
        """Test election string representation"""
        election = Election.objects.create(**self.election_data)
        expected_str = f"{election.title} ({election.get_election_type_display()})"
        self.assertEqual(str(election), expected_str)
    
    def test_is_registration_open_property(self):
        """Test is_registration_open property"""
        # Future registration
        future_election = Election.objects.create(
            **{**self.election_data, 
               'registration_start_date': timezone.now() + timedelta(days=1),
               'registration_end_date': timezone.now() + timedelta(days=30)}
        )
        self.assertFalse(future_election.is_registration_open)
        
        # Current registration
        current_election = Election.objects.create(
            **{**self.election_data,
               'title': 'Current Election',
               'registration_start_date': timezone.now() - timedelta(days=1),
               'registration_end_date': timezone.now() + timedelta(days=30)}
        )
        self.assertTrue(current_election.is_registration_open)
        
        # Past registration
        past_election = Election.objects.create(
            **{**self.election_data,
               'title': 'Past Election',
               'registration_start_date': timezone.now() - timedelta(days=30),
               'registration_end_date': timezone.now() - timedelta(days=1)}
        )
        self.assertFalse(past_election.is_registration_open)
    
    def test_is_voting_open_property(self):
        """Test is_voting_open property"""
        # Active election with current voting period
        active_election = Election.objects.create(
            **{**self.election_data,
               'status': 'active',
               'voting_start_date': timezone.now() - timedelta(hours=1),
               'voting_end_date': timezone.now() + timedelta(hours=1)}
        )
        self.assertTrue(active_election.is_voting_open)
        
        # Draft election (not active)
        draft_election = Election.objects.create(
            **{**self.election_data,
               'title': 'Draft Election',
               'status': 'draft',
               'voting_start_date': timezone.now() - timedelta(hours=1),
               'voting_end_date': timezone.now() + timedelta(hours=1)}
        )
        self.assertFalse(draft_election.is_voting_open)
    
    def test_voter_turnout_percentage(self):
        """Test voter turnout percentage calculation"""
        election = Election.objects.create(**self.election_data)
        
        # No voters
        self.assertEqual(election.voter_turnout_percentage, 0)
        
        # With voters
        election.total_eligible_voters = 1000
        election.total_votes_cast = 750
        election.save()
        
        self.assertEqual(election.voter_turnout_percentage, 75.0)


class ElectionPositionTest(TestCase):
    """Test cases for ElectionPosition model"""
    
    def setUp(self):
        self.commission_user = User.objects.create_user(
            username='commission',
            user_type='electoral_commission'
        )
        
        self.election = Election.objects.create(
            title='Test Election',
            description='Test',
            election_type='presidential',
            registration_start_date=timezone.now() + timedelta(days=1),
            registration_end_date=timezone.now() + timedelta(days=30),
            voting_start_date=timezone.now() + timedelta(days=31),
            voting_end_date=timezone.now() + timedelta(days=32),
            created_by=self.commission_user
        )
    
    def test_create_election_position(self):
        """Test creating an election position"""
        position = ElectionPosition.objects.create(
            election=self.election,
            title='President',
            description='President of the Republic',
            minimum_age=35,
            available_seats=1
        )
        
        self.assertEqual(position.election, self.election)
        self.assertEqual(position.title, 'President')
        self.assertEqual(position.minimum_age, 35)
        self.assertEqual(position.max_votes_per_voter, 1)
        self.assertTrue(position.is_active)
    
    def test_position_str_representation(self):
        """Test position string representation"""
        position = ElectionPosition.objects.create(
            election=self.election,
            title='President'
        )
        expected_str = f"President - {self.election.title}"
        self.assertEqual(str(position), expected_str)
    
    def test_unique_position_per_election(self):
        """Test that position titles are unique per election"""
        ElectionPosition.objects.create(
            election=self.election,
            title='President'
        )
        
        # Creating another position with same title should raise error
        with self.assertRaises(Exception):
            ElectionPosition.objects.create(
                election=self.election,
                title='President'
            )


class ElectionCandidateTest(TestCase):
    """Test cases for ElectionCandidate model"""
    
    def setUp(self):
        self.commission_user = User.objects.create_user(
            username='commission',
            user_type='electoral_commission'
        )
        
        self.candidate_user = User.objects.create_user(
            username='candidate',
            user_type='candidate',
            first_name='John',
            last_name='Doe'
        )
        
        self.election = Election.objects.create(
            title='Test Election',
            description='Test',
            election_type='presidential',
            registration_start_date=timezone.now() + timedelta(days=1),
            registration_end_date=timezone.now() + timedelta(days=30),
            voting_start_date=timezone.now() + timedelta(days=31),
            voting_end_date=timezone.now() + timedelta(days=32),
            created_by=self.commission_user
        )
        
        self.position = ElectionPosition.objects.create(
            election=self.election,
            title='President'
        )
    
    def test_create_election_candidate(self):
        """Test creating an election candidate"""
        candidate = ElectionCandidate.objects.create(
            election=self.election,
            position=self.position,
            candidate=self.candidate_user,
            campaign_name='Vote for Change',
            campaign_slogan='A Better Tomorrow',
            ballot_number=1
        )
        
        self.assertEqual(candidate.election, self.election)
        self.assertEqual(candidate.position, self.position)
        self.assertEqual(candidate.candidate, self.candidate_user)
        self.assertEqual(candidate.status, 'registered')
        self.assertEqual(candidate.total_votes, 0)
    
    def test_candidate_str_representation(self):
        """Test candidate string representation"""
        candidate = ElectionCandidate.objects.create(
            election=self.election,
            position=self.position,
            candidate=self.candidate_user
        )
        expected_str = f"{self.candidate_user.get_full_name()} - {self.position.title}"
        self.assertEqual(str(candidate), expected_str)
    
    def test_unique_candidate_per_position(self):
        """Test that a candidate can only register once per position"""
        ElectionCandidate.objects.create(
            election=self.election,
            position=self.position,
            candidate=self.candidate_user
        )
        
        # Creating another candidacy for same candidate and position should raise error
        with self.assertRaises(Exception):
            ElectionCandidate.objects.create(
                election=self.election,
                position=self.position,
                candidate=self.candidate_user
            )


class ElectionConstituencyTest(TestCase):
    """Test cases for ElectionConstituency model"""
    
    def setUp(self):
        self.commission_user = User.objects.create_user(
            username='commission',
            user_type='electoral_commission'
        )
        
        self.election = Election.objects.create(
            title='Test Election',
            description='Test',
            election_type='parliamentary',
            registration_start_date=timezone.now() + timedelta(days=1),
            registration_end_date=timezone.now() + timedelta(days=30),
            voting_start_date=timezone.now() + timedelta(days=31),
            voting_end_date=timezone.now() + timedelta(days=32),
            created_by=self.commission_user
        )
    
    def test_create_constituency(self):
        """Test creating an election constituency"""
        constituency = ElectionConstituency.objects.create(
            election=self.election,
            name='Central District',
            code='CD001',
            description='Central business district',
            region='Metro',
            registered_voters_count=5000
        )
        
        self.assertEqual(constituency.election, self.election)
        self.assertEqual(constituency.name, 'Central District')
        self.assertEqual(constituency.code, 'CD001')
        self.assertEqual(constituency.registered_voters_count, 5000)
    
    def test_constituency_str_representation(self):
        """Test constituency string representation"""
        constituency = ElectionConstituency.objects.create(
            election=self.election,
            name='Central District',
            code='CD001'
        )
        expected_str = f"Central District (CD001)"
        self.assertEqual(str(constituency), expected_str)


class PollingStationTest(TestCase):
    """Test cases for PollingStation model"""
    
    def setUp(self):
        self.commission_user = User.objects.create_user(
            username='commission',
            user_type='electoral_commission'
        )
        
        self.official_user = User.objects.create_user(
            username='official',
            user_type='voter_official'
        )
        
        self.election = Election.objects.create(
            title='Test Election',
            description='Test',
            election_type='parliamentary',
            registration_start_date=timezone.now() + timedelta(days=1),
            registration_end_date=timezone.now() + timedelta(days=30),
            voting_start_date=timezone.now() + timedelta(days=31),
            voting_end_date=timezone.now() + timedelta(days=32),
            created_by=self.commission_user
        )
        
        self.constituency = ElectionConstituency.objects.create(
            election=self.election,
            name='Central District',
            code='CD001'
        )
    
    def test_create_polling_station(self):
        """Test creating a polling station"""
        station = PollingStation.objects.create(
            constituency=self.constituency,
            name='Central Primary School',
            code='CPS001',
            address='123 Main Street, Central District',
            capacity=800,
            presiding_officer=self.official_user
        )
        
        self.assertEqual(station.constituency, self.constituency)
        self.assertEqual(station.name, 'Central Primary School')
        self.assertEqual(station.capacity, 800)
        self.assertEqual(station.presiding_officer, self.official_user)
        self.assertTrue(station.is_active)
    
    def test_polling_station_str_representation(self):
        """Test polling station string representation"""
        station = PollingStation.objects.create(
            constituency=self.constituency,
            name='Central Primary School',
            code='CPS001',
            address='123 Main Street'
        )
        expected_str = f"Central Primary School - {self.constituency.name}"
        self.assertEqual(str(station), expected_str)


class ElectionResultTest(TestCase):
    """Test cases for ElectionResult model"""
    
    def setUp(self):
        self.commission_user = User.objects.create_user(
            username='commission',
            user_type='electoral_commission'
        )
        
        self.candidate_user = User.objects.create_user(
            username='candidate',
            user_type='candidate',
            first_name='John',
            last_name='Doe'
        )
        
        self.election = Election.objects.create(
            title='Test Election',
            description='Test',
            election_type='presidential',
            registration_start_date=timezone.now() - timedelta(days=30),
            registration_end_date=timezone.now() - timedelta(days=10),
            voting_start_date=timezone.now() - timedelta(days=5),
            voting_end_date=timezone.now() - timedelta(days=1),
            created_by=self.commission_user,
            status='completed'
        )
        
        self.position = ElectionPosition.objects.create(
            election=self.election,
            title='President'
        )
        
        self.candidate = ElectionCandidate.objects.create(
            election=self.election,
            position=self.position,
            candidate=self.candidate_user,
            status='approved'
        )
    
    def test_create_election_result(self):
        """Test creating an election result"""
        result = ElectionResult.objects.create(
            election=self.election,
            position=self.position,
            candidate=self.candidate,
            total_votes=15000,
            vote_percentage=Decimal('65.50'),
            rank=1,
            is_winner=True,
            blockchain_hash='0x123456789abcdef',
            is_verified=True
        )
        
        self.assertEqual(result.election, self.election)
        self.assertEqual(result.candidate, self.candidate)
        self.assertEqual(result.total_votes, 15000)
        self.assertEqual(result.vote_percentage, Decimal('65.50'))
        self.assertEqual(result.rank, 1)
        self.assertTrue(result.is_winner)
        self.assertTrue(result.is_verified)
    
    def test_result_str_representation(self):
        """Test result string representation"""
        result = ElectionResult.objects.create(
            election=self.election,
            position=self.position,
            candidate=self.candidate,
            total_votes=15000,
            vote_percentage=Decimal('65.50'),
            rank=1
        )
        expected_str = f"{self.candidate} - 15000 votes (65.50%)"
        self.assertEqual(str(result), expected_str)


class ElectionAuditLogTest(TestCase):
    """Test cases for ElectionAuditLog model"""
    
    def setUp(self):
        self.commission_user = User.objects.create_user(
            username='commission',
            user_type='electoral_commission'
        )
        
        self.election = Election.objects.create(
            title='Test Election',
            description='Test',
            election_type='presidential',
            registration_start_date=timezone.now() + timedelta(days=1),
            registration_end_date=timezone.now() + timedelta(days=30),
            voting_start_date=timezone.now() + timedelta(days=31),
            voting_end_date=timezone.now() + timedelta(days=32),
            created_by=self.commission_user
        )
    
    def test_create_audit_log(self):
        """Test creating an audit log entry"""
        audit_log = ElectionAuditLog.objects.create(
            election=self.election,
            action='election_created',
            description='Election was created by commission user',
            performed_by=self.commission_user,
            ip_address='127.0.0.1',
            metadata={'additional_info': 'test data'}
        )
        
        self.assertEqual(audit_log.election, self.election)
        self.assertEqual(audit_log.action, 'election_created')
        self.assertEqual(audit_log.performed_by, self.commission_user)
        self.assertEqual(audit_log.ip_address, '127.0.0.1')
        self.assertIsNotNone(audit_log.timestamp)
    
    def test_audit_log_str_representation(self):
        """Test audit log string representation"""
        audit_log = ElectionAuditLog.objects.create(
            election=self.election,
            action='election_created',
            description='Test audit log'
        )
        expected_str = f"{self.election.title} - Election Created"
        self.assertEqual(str(audit_log), expected_str)


class ElectionNotificationTest(TestCase):
    """Test cases for ElectionNotification model"""
    
    def setUp(self):
        self.commission_user = User.objects.create_user(
            username='commission',
            user_type='electoral_commission'
        )
        
        self.voter_user = User.objects.create_user(
            username='voter',
            user_type='voter'
        )
        
        self.election = Election.objects.create(
            title='Test Election',
            description='Test',
            election_type='presidential',
            registration_start_date=timezone.now() + timedelta(days=1),
            registration_end_date=timezone.now() + timedelta(days=30),
            voting_start_date=timezone.now() + timedelta(days=31),
            voting_end_date=timezone.now() + timedelta(days=32),
            created_by=self.commission_user
        )
    
    def test_create_notification(self):
        """Test creating an election notification"""
        notification = ElectionNotification.objects.create(
            election=self.election,
            notification_type='registration_open',
            title='Registration Now Open',
            message='Candidate registration is now open for the upcoming election.',
            target_user_types=['candidate', 'voter'],
            scheduled_for=timezone.now() + timedelta(hours=1)
        )
        
        self.assertEqual(notification.election, self.election)
        self.assertEqual(notification.notification_type, 'registration_open')
        self.assertEqual(notification.title, 'Registration Now Open')
        self.assertFalse(notification.is_sent)
        self.assertEqual(notification.target_user_types, ['candidate', 'voter'])
    
    def test_notification_str_representation(self):
        """Test notification string representation"""
        notification = ElectionNotification.objects.create(
            election=self.election,
            notification_type='registration_open',
            title='Registration Now Open',
            message='Test message'
        )
        expected_str = f"Registration Now Open - {self.election.title}"
        self.assertEqual(str(notification), expected_str)
    
    def test_notification_target_users(self):
        """Test notification target users many-to-many relationship"""
        notification = ElectionNotification.objects.create(
            election=self.election,
            notification_type='voting_open',
            title='Voting Now Open',
            message='Voting is now open'
        )
        
        # Add target users
        notification.target_users.add(self.voter_user)
        
        self.assertIn(self.voter_user, notification.target_users.all())


class ElectionBusinessLogicTest(TestCase):
    """Test business logic and complex scenarios"""
    
    def setUp(self):
        self.commission_user = User.objects.create_user(
            username='commission',
            user_type='electoral_commission'
        )
        
        self.candidate1 = User.objects.create_user(
            username='candidate1',
            user_type='candidate',
            first_name='John',
            last_name='Doe'
        )
        
        self.candidate2 = User.objects.create_user(
            username='candidate2',
            user_type='candidate',
            first_name='Jane',
            last_name='Smith'
        )
    
    def test_election_lifecycle(self):
        """Test complete election lifecycle"""
        # Create election
        election = Election.objects.create(
            title='Presidential Election 2024',
            description='National presidential election',
            election_type='presidential',
            registration_start_date=timezone.now() - timedelta(days=30),
            registration_end_date=timezone.now() - timedelta(days=10),
            voting_start_date=timezone.now() - timedelta(days=5),
            voting_end_date=timezone.now() - timedelta(days=1),
            created_by=self.commission_user
        )
        
        # Create position
        position = ElectionPosition.objects.create(
            election=election,
            title='President',
            minimum_age=35
        )
        
        # Register candidates
        candidate1 = ElectionCandidate.objects.create(
            election=election,
            position=position,
            candidate=self.candidate1,
            status='approved',
            ballot_number=1
        )
        
        candidate2 = ElectionCandidate.objects.create(
            election=election,
            position=position,
            candidate=self.candidate2,
            status='approved',
            ballot_number=2
        )
        
        # Create results
        result1 = ElectionResult.objects.create(
            election=election,
            position=position,
            candidate=candidate1,
            total_votes=15000,
            vote_percentage=Decimal('60.00'),
            rank=1,
            is_winner=True
        )
        
        result2 = ElectionResult.objects.create(
            election=election,
            position=position,
            candidate=candidate2,
            total_votes=10000,
            vote_percentage=Decimal('40.00'),
            rank=2,
            is_winner=False
        )
        
        # Verify election state
        self.assertEqual(election.candidates.count(), 2)
        self.assertEqual(election.results.count(), 2)
        self.assertTrue(election.is_completed)
        
        # Verify winner
        winner = election.results.filter(is_winner=True).first()
        self.assertEqual(winner.candidate, candidate1)
        self.assertEqual(winner.total_votes, 15000)


class ElectionValidationTest(TestCase):
    """Test model validation and constraints"""
    
    def setUp(self):
        self.commission_user = User.objects.create_user(
            username='commission',
            user_type='electoral_commission'
        )
    
    def test_election_date_validation(self):
        """Test election date logical validation"""
        # This would typically be handled by custom model validation
        # For now, we test that the model accepts valid dates
        election = Election.objects.create(
            title='Test Election',
            description='Test',
            election_type='presidential',
            registration_start_date=timezone.now() + timedelta(days=1),
            registration_end_date=timezone.now() + timedelta(days=30),
            voting_start_date=timezone.now() + timedelta(days=31),
            voting_end_date=timezone.now() + timedelta(days=32),
            created_by=self.commission_user
        )
        
        self.assertIsNotNone(election.id)
        self.assertTrue(election.registration_start_date < election.registration_end_date)
        self.assertTrue(election.voting_start_date < election.voting_end_date)
    
    def test_election_status_choices(self):
        """Test election status field accepts only valid choices"""
        valid_statuses = ['draft', 'scheduled', 'active', 'completed', 'cancelled']
        
        for status in valid_statuses:
            election = Election.objects.create(
                title=f'Test Election {status}',
                description='Test',
                election_type='presidential',
                status=status,
                registration_start_date=timezone.now() + timedelta(days=1),
                registration_end_date=timezone.now() + timedelta(days=30),
                voting_start_date=timezone.now() + timedelta(days=31),
                voting_end_date=timezone.now() + timedelta(days=32),
                created_by=self.commission_user
            )
            self.assertEqual(election.status, status)
