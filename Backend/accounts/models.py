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


class RoleApplication(models.Model):
    """
    Track role transition applications with document requirements
    """
    APPLICATION_STATUS = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('documents_required', 'Documents Required'),
    ]
    
    APPLICATION_TYPES = [
        ('voter', 'Voter Registration'),
        ('candidate', 'Candidate Application'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_applications')
    application_type = models.CharField(max_length=20, choices=APPLICATION_TYPES)
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='pending')
    application_date = models.DateTimeField(default=timezone.now)
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_applications'
    )
    review_date = models.DateTimeField(blank=True, null=True)
    review_notes = models.TextField(blank=True, null=True)
    
    # Additional fields for candidate applications
    political_party = models.CharField(max_length=100, blank=True, null=True)
    campaign_slogan = models.CharField(max_length=200, blank=True, null=True)
    manifesto = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'role_applications'
        ordering = ['-application_date']
        unique_together = ['user', 'application_type', 'status']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_application_type_display()} ({self.get_status_display()})"


class ApplicationDocument(models.Model):
    """
    Store documents uploaded for role applications
    """
    DOCUMENT_TYPES = [
        ('national_id', 'National ID Card'),
        ('passport', 'Passport'),
        ('birth_certificate', 'Birth Certificate'),
        ('proof_of_residence', 'Proof of Residence'),
        ('educational_certificate', 'Educational Certificate'),
        ('criminal_background_check', 'Criminal Background Check'),
        ('tax_clearance', 'Tax Clearance Certificate'),
        ('party_nomination', 'Political Party Nomination'),
        ('affidavit', 'Sworn Affidavit'),
        ('medical_certificate', 'Medical Certificate'),
        ('other', 'Other Document'),
    ]
    
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    application = models.ForeignKey(RoleApplication, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='application_documents/%Y/%m/')
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()  # Size in bytes
    mime_type = models.CharField(max_length=100)
    
    # Verification fields
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_documents'
    )
    verification_date = models.DateTimeField(blank=True, null=True)
    verification_notes = models.TextField(blank=True, null=True)
    
    # Metadata
    upload_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateField(blank=True, null=True)  # For documents with expiry
    
    class Meta:
        db_table = 'application_documents'
        ordering = ['-upload_date']
        unique_together = ['application', 'document_type']
    
    def __str__(self):
        return f"{self.application.user.username} - {self.get_document_type_display()}"
    
    @property
    def file_size_mb(self):
        """Return file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def is_image(self):
        """Check if document is an image"""
        return self.mime_type.startswith('image/')
    
    @property
    def is_pdf(self):
        """Check if document is a PDF"""
        return self.mime_type == 'application/pdf'


class DocumentRequirement(models.Model):
    """
    Define document requirements for different application types
    """
    application_type = models.CharField(max_length=20, choices=RoleApplication.APPLICATION_TYPES)
    document_type = models.CharField(max_length=30, choices=ApplicationDocument.DOCUMENT_TYPES)
    is_required = models.BooleanField(default=True)
    description = models.TextField(help_text="Description of what this document should contain")
    max_file_size_mb = models.PositiveIntegerField(default=5)  # Max file size in MB
    allowed_formats = models.JSONField(default=list)  # List of allowed file formats
    
    class Meta:
        db_table = 'document_requirements'
        unique_together = ['application_type', 'document_type']
    
    def __str__(self):
        return f"{self.get_application_type_display()} - {self.get_document_type_display()}"


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
        ('application_submitted', 'Application Submitted'),
        ('document_uploaded', 'Document Uploaded'),
        ('application_reviewed', 'Application Reviewed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=25, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(blank=True, null=True)  # Store additional activity data
    
    class Meta:
        db_table = 'user_activities'
        ordering = ['-timestamp']
