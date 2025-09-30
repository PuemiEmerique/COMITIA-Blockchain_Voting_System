"""
COMITIA Elections Models
Handles election creation, management, and candidate assignments
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Election(models.Model):
    """
    Main Election model
    """
    ELECTION_TYPES = [
        ('presidential', 'Presidential'),
        ('parliamentary', 'Parliamentary'),
        ('local', 'Local Government'),
        ('referendum', 'Referendum'),
        ('primary', 'Primary Election'),
    ]
    
    ELECTION_STATUS = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    election_type = models.CharField(max_length=20, choices=ELECTION_TYPES)
    status = models.CharField(max_length=20, choices=ELECTION_STATUS, default='draft')
    
    # Dates and Timing
    registration_start_date = models.DateTimeField()
    registration_end_date = models.DateTimeField()
    voting_start_date = models.DateTimeField()
    voting_end_date = models.DateTimeField()
    
    # Election Configuration
    max_candidates_per_position = models.PositiveIntegerField(default=10)
    allow_multiple_votes = models.BooleanField(default=False)  # For positions with multiple seats
    require_biometric_auth = models.BooleanField(default=True)
    
    # Blockchain Configuration
    blockchain_contract_address = models.CharField(max_length=42, blank=True, null=True)
    blockchain_network = models.CharField(max_length=50, default='sepolia')
    
    # Management
    created_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.PROTECT, 
        related_name='created_elections'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Results
    total_votes_cast = models.PositiveIntegerField(default=0)
    total_eligible_voters = models.PositiveIntegerField(default=0)
    results_published = models.BooleanField(default=False)
    results_published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'elections'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_election_type_display()})"
    
    @property
    def is_registration_open(self):
        now = timezone.now()
        return self.registration_start_date <= now <= self.registration_end_date
    
    @property
    def is_voting_open(self):
        now = timezone.now()
        return self.voting_start_date <= now <= self.voting_end_date and self.status == 'active'
    
    @property
    def is_completed(self):
        return self.status == 'completed' or timezone.now() > self.voting_end_date
    
    @property
    def voter_turnout_percentage(self):
        if self.total_eligible_voters > 0:
            return (self.total_votes_cast / self.total_eligible_voters) * 100
        return 0


class ElectionPosition(models.Model):
    """
    Positions available in an election (e.g., President, Governor, Senator)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='positions')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    # Position Configuration
    max_votes_per_voter = models.PositiveIntegerField(default=1)  # How many candidates a voter can select
    available_seats = models.PositiveIntegerField(default=1)  # How many people can win this position
    
    # Requirements
    minimum_age = models.PositiveIntegerField(default=18)
    citizenship_required = models.BooleanField(default=True)
    
    # Order and Display
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'election_positions'
        ordering = ['display_order', 'title']
        unique_together = ['election', 'title']
    
    def __str__(self):
        return f"{self.title} - {self.election.title}"


class ElectionCandidate(models.Model):
    """
    Candidates registered for specific positions in elections
    """
    CANDIDATE_STATUS = [
        ('registered', 'Registered'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
        ('disqualified', 'Disqualified'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    position = models.ForeignKey(ElectionPosition, on_delete=models.CASCADE, related_name='candidates')
    candidate = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='election_candidacies'
    )
    
    # Registration Information
    registration_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=CANDIDATE_STATUS, default='registered')
    
    # Campaign Information
    campaign_name = models.CharField(max_length=200, blank=True, null=True)
    campaign_slogan = models.CharField(max_length=300, blank=True, null=True)
    campaign_logo = models.ImageField(upload_to='campaign_logos/', blank=True, null=True)
    
    # Ballot Information
    ballot_number = models.PositiveIntegerField(blank=True, null=True)
    ballot_symbol = models.CharField(max_length=50, blank=True, null=True)
    
    # Results
    total_votes = models.PositiveIntegerField(default=0)
    vote_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Management
    approved_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_election_candidates'
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'election_candidates'
        unique_together = ['election', 'position', 'candidate']
        ordering = ['ballot_number', 'candidate__first_name']
    
    def __str__(self):
        return f"{self.candidate.get_full_name()} - {self.position.title}"


class ElectionConstituency(models.Model):
    """
    Geographic constituencies for elections
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='constituencies')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    
    # Geographic Information
    region = models.CharField(max_length=100, blank=True, null=True)
    state_province = models.CharField(max_length=100, blank=True, null=True)
    
    # Voter Information
    registered_voters_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'election_constituencies'
        unique_together = ['election', 'code']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class PollingStation(models.Model):
    """
    Physical or virtual polling stations
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    constituency = models.ForeignKey(ElectionConstituency, on_delete=models.CASCADE, related_name='polling_stations')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    
    # Location Information
    address = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    
    # Capacity and Management
    capacity = models.PositiveIntegerField(default=500)
    assigned_voters_count = models.PositiveIntegerField(default=0)
    
    # Officials
    presiding_officer = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='presided_polling_stations'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'polling_stations'
        unique_together = ['constituency', 'code']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.constituency.name}"


class ElectionResult(models.Model):
    """
    Final election results
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='results')
    position = models.ForeignKey(ElectionPosition, on_delete=models.CASCADE, related_name='results')
    candidate = models.ForeignKey(ElectionCandidate, on_delete=models.CASCADE, related_name='results')
    
    # Vote Counts
    total_votes = models.PositiveIntegerField()
    vote_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Ranking
    rank = models.PositiveIntegerField()
    is_winner = models.BooleanField(default=False)
    
    # Blockchain Verification
    blockchain_hash = models.CharField(max_length=66, blank=True, null=True)  # Transaction hash
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    calculated_at = models.DateTimeField(default=timezone.now)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'election_results'
        unique_together = ['election', 'position', 'candidate']
        ordering = ['position', 'rank']
    
    def __str__(self):
        return f"{self.candidate} - {self.total_votes} votes ({self.vote_percentage}%)"


class ElectionAuditLog(models.Model):
    """
    Audit log for election activities
    """
    AUDIT_ACTIONS = [
        ('election_created', 'Election Created'),
        ('election_updated', 'Election Updated'),
        ('candidate_registered', 'Candidate Registered'),
        ('candidate_approved', 'Candidate Approved'),
        ('candidate_rejected', 'Candidate Rejected'),
        ('voting_started', 'Voting Started'),
        ('voting_ended', 'Voting Ended'),
        ('results_calculated', 'Results Calculated'),
        ('results_published', 'Results Published'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=30, choices=AUDIT_ACTIONS)
    description = models.TextField()
    
    # User and System Information
    performed_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='election_audit_actions'
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Additional Data
    metadata = models.JSONField(blank=True, null=True)
    
    # Timestamp
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'election_audit_logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.election.title} - {self.get_action_display()}"


class ElectionNotification(models.Model):
    """
    Notifications related to elections
    """
    NOTIFICATION_TYPES = [
        ('election_created', 'Election Created'),
        ('registration_open', 'Registration Open'),
        ('registration_closing', 'Registration Closing Soon'),
        ('voting_open', 'Voting Open'),
        ('voting_closing', 'Voting Closing Soon'),
        ('results_available', 'Results Available'),
        ('candidate_approved', 'Candidate Approved'),
        ('candidate_rejected', 'Candidate Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Targeting
    target_user_types = models.JSONField(default=list)  # List of user types to notify
    target_users = models.ManyToManyField('accounts.User', blank=True)  # Specific users
    
    # Delivery
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    
    # Scheduling
    scheduled_for = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'election_notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.election.title}"
