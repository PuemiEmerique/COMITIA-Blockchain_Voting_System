"""
COMITIA User Models
Supports 5 user types: Citizens, Voters, Candidates, Voter Officials, Electoral Commission
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid


class User(AbstractUser):
    """
    Custom User model supporting 5 user types in COMITIA system
    """
    
    USER_TYPES = [
        ('citizen', 'Citizen'),
        ('voter', 'Voter'),
        ('candidate', 'Candidate'),
        ('voter_official', 'Voter Official'),
        ('electoral_commission', 'Electoral Commission'),
    ]
    
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='citizen')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    national_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Verification and Status
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    is_biometric_registered = models.BooleanField(default=False)
    registration_date = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Profile Information
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Blockchain Information
    ethereum_address = models.CharField(max_length=42, blank=True, null=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def is_citizen(self):
        return self.user_type == 'citizen'
    
    @property
    def is_voter(self):
        return self.user_type == 'voter'
    
    @property
    def is_candidate(self):
        return self.user_type == 'candidate'
    
    @property
    def is_voter_official(self):
        return self.user_type == 'voter_official'
    
    @property
    def is_electoral_commission(self):
        return self.user_type == 'electoral_commission'
    
    @property
    def can_vote(self):
        """Check if user can vote (voters and candidates can vote)"""
        return self.user_type in ['voter', 'candidate'] and self.verification_status == 'approved'
    
    @property
    def can_manage_elections(self):
        """Check if user can manage elections"""
        return self.user_type == 'electoral_commission'
    
    @property
    def can_manage_voters(self):
        """Check if user can manage voter registrations"""
        return self.user_type in ['voter_official', 'electoral_commission']


class CitizenProfile(models.Model):
    """
    Extended profile for Citizens
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='citizen_profile')
    occupation = models.CharField(max_length=100, blank=True, null=True)
    education_level = models.CharField(max_length=50, blank=True, null=True)
    voter_pre_enrollment_date = models.DateTimeField(blank=True, null=True)
    voter_pre_enrollment_status = models.CharField(
        max_length=20, 
        choices=[('not_applied', 'Not Applied'), ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='not_applied'
    )
    
    class Meta:
        db_table = 'citizen_profiles'


class VoterProfile(models.Model):
    """
    Extended profile for Voters
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='voter_profile')
    voter_id = models.CharField(max_length=20, unique=True)
    polling_station = models.CharField(max_length=100, blank=True, null=True)
    constituency = models.CharField(max_length=100, blank=True, null=True)
    voter_card_issued = models.BooleanField(default=False)
    voter_card_number = models.CharField(max_length=20, blank=True, null=True)
    registration_completed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='registered_voters'
    )
    
    class Meta:
        db_table = 'voter_profiles'


class CandidateProfile(models.Model):
    """
    Extended profile for Candidates
    """
    CANDIDATE_STATUS = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disqualified', 'Disqualified'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    candidate_id = models.CharField(max_length=20, unique=True)
    political_party = models.CharField(max_length=100, blank=True, null=True)
    campaign_slogan = models.CharField(max_length=200, blank=True, null=True)
    manifesto = models.TextField(blank=True, null=True)
    application_status = models.CharField(max_length=20, choices=CANDIDATE_STATUS, default='pending')
    application_date = models.DateTimeField(default=timezone.now)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='approved_candidates'
    )
    
    class Meta:
        db_table = 'candidate_profiles'


class VoterOfficialProfile(models.Model):
    """
    Extended profile for Voter Officials
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='voter_official_profile')
    official_id = models.CharField(max_length=20, unique=True)
    assigned_region = models.CharField(max_length=100, blank=True, null=True)
    registration_center = models.CharField(max_length=100, blank=True, null=True)
    appointment_date = models.DateTimeField(default=timezone.now)
    appointed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='appointed_officials'
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'voter_official_profiles'


class ElectoralCommissionProfile(models.Model):
    """
    Extended profile for Electoral Commission members
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='electoral_commission_profile')
    commission_id = models.CharField(max_length=20, unique=True)
    position = models.CharField(max_length=100, blank=True, null=True)  # Chairman, Commissioner, etc.
    jurisdiction = models.CharField(max_length=100, blank=True, null=True)
    appointment_date = models.DateTimeField(default=timezone.now)
    term_end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'electoral_commission_profiles'


class BiometricData(models.Model):
    """
    Store biometric data for users
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='biometric_data')
    face_encoding = models.JSONField(blank=True, null=True)  # Store face recognition encoding
    face_image_path = models.CharField(max_length=255, blank=True, null=True)
    fingerprint_template = models.JSONField(blank=True, null=True)  # Store fingerprint template
    registration_date = models.DateTimeField(default=timezone.now)
    registered_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='registered_biometrics'
    )
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'biometric_data'


class UserActivity(models.Model):
    """
    Track user activities for audit purposes
    """
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('vote_cast', 'Vote Cast'),
        ('profile_update', 'Profile Update'),
        ('biometric_auth', 'Biometric Authentication'),
        ('election_created', 'Election Created'),
        ('candidate_approved', 'Candidate Approved'),
        ('voter_registered', 'Voter Registered'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(blank=True, null=True)  # Store additional activity data
    
    class Meta:
        db_table = 'user_activities'
        ordering = ['-timestamp']
