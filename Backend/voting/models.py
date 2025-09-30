"""
COMITIA Voting Models
Handles vote casting, storage, and blockchain integration
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid
import json


class Vote(models.Model):
    """
    Individual vote record
    """
    VOTE_STATUS = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted to Blockchain'),
        ('confirmed', 'Confirmed on Blockchain'),
        ('failed', 'Failed'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey('elections.Election', on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='cast_votes')
    
    # Vote Details
    position = models.ForeignKey('elections.ElectionPosition', on_delete=models.CASCADE)
    candidate = models.ForeignKey('elections.ElectionCandidate', on_delete=models.CASCADE)
    
    # Blockchain Information
    blockchain_hash = models.CharField(max_length=66, blank=True, null=True)  # Transaction hash
    block_number = models.PositiveIntegerField(blank=True, null=True)
    gas_used = models.PositiveIntegerField(blank=True, null=True)
    
    # Vote Verification
    vote_hash = models.CharField(max_length=64, unique=True)  # SHA-256 hash of vote data
    encrypted_vote = models.TextField()  # Encrypted vote data
    verification_code = models.CharField(max_length=20, unique=True)  # For voter verification
    
    # Status and Timing
    status = models.CharField(max_length=20, choices=VOTE_STATUS, default='pending')
    cast_at = models.DateTimeField(default=timezone.now)
    submitted_to_blockchain_at = models.DateTimeField(blank=True, null=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    
    # Authentication Information
    biometric_verified = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # Metadata
    metadata = models.JSONField(default=dict)  # Additional vote metadata
    
    class Meta:
        db_table = 'votes'
        unique_together = ['election', 'voter', 'position']  # One vote per position per voter
        ordering = ['-cast_at']
    
    def __str__(self):
        return f"Vote by {self.voter.username} in {self.election.title}"
    
    @property
    def is_confirmed(self):
        return self.status == 'confirmed'
    
    @property
    def is_on_blockchain(self):
        return self.blockchain_hash is not None


class VotingSession(models.Model):
    """
    Voting session to track user's voting process
    """
    SESSION_STATUS = [
        ('started', 'Started'),
        ('biometric_verified', 'Biometric Verified'),
        ('voting', 'Voting in Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey('elections.Election', on_delete=models.CASCADE, related_name='voting_sessions')
    voter = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='voting_sessions')
    
    # Session Information
    session_token = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='started')
    
    # Biometric Verification
    biometric_verified = models.BooleanField(default=False)
    biometric_verification_time = models.DateTimeField(blank=True, null=True)
    
    # Timing
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField()  # Session expiry time
    
    # Network Information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # Vote Progress
    total_positions = models.PositiveIntegerField(default=0)
    positions_voted = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'voting_sessions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Voting session for {self.voter.username} in {self.election.title}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_complete(self):
        return self.status == 'completed'


class VoteVerification(models.Model):
    """
    Vote verification records for transparency
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vote = models.OneToOneField(Vote, on_delete=models.CASCADE, related_name='verification')
    
    # Verification Details
    verification_hash = models.CharField(max_length=64)  # Hash for public verification
    merkle_root = models.CharField(max_length=64, blank=True, null=True)  # Merkle tree root
    merkle_proof = models.JSONField(blank=True, null=True)  # Merkle proof path
    
    # Blockchain Verification
    blockchain_verified = models.BooleanField(default=False)
    blockchain_verification_time = models.DateTimeField(blank=True, null=True)
    
    # Public Verification
    public_verification_code = models.CharField(max_length=32, unique=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'vote_verifications'
    
    def __str__(self):
        return f"Verification for vote {self.vote.verification_code}"


class BlockchainTransaction(models.Model):
    """
    Blockchain transaction records
    """
    TRANSACTION_TYPES = [
        ('vote_cast', 'Vote Cast'),
        ('election_created', 'Election Created'),
        ('results_published', 'Results Published'),
        ('contract_deployed', 'Contract Deployed'),
    ]
    
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_hash = models.CharField(max_length=66, unique=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    
    # Blockchain Details
    block_number = models.PositiveIntegerField(blank=True, null=True)
    block_hash = models.CharField(max_length=66, blank=True, null=True)
    gas_used = models.PositiveIntegerField(blank=True, null=True)
    gas_price = models.BigIntegerField(blank=True, null=True)
    
    # Transaction Data
    from_address = models.CharField(max_length=42)
    to_address = models.CharField(max_length=42)
    value = models.BigIntegerField(default=0)  # Wei amount
    input_data = models.TextField(blank=True, null=True)  # Transaction input data
    
    # Related Objects
    election = models.ForeignKey('elections.Election', on_delete=models.CASCADE, blank=True, null=True)
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, blank=True, null=True)
    
    # Timing
    created_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(blank=True, null=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    
    # Error Information
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'blockchain_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.transaction_hash[:10]}..."


class VoteAuditLog(models.Model):
    """
    Audit log for voting activities
    """
    AUDIT_ACTIONS = [
        ('session_started', 'Voting Session Started'),
        ('biometric_verified', 'Biometric Verified'),
        ('vote_cast', 'Vote Cast'),
        ('vote_submitted', 'Vote Submitted to Blockchain'),
        ('vote_confirmed', 'Vote Confirmed on Blockchain'),
        ('vote_verified', 'Vote Verified by Voter'),
        ('session_completed', 'Voting Session Completed'),
        ('session_abandoned', 'Voting Session Abandoned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey('elections.Election', on_delete=models.CASCADE, related_name='vote_audit_logs')
    voter = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='vote_audit_logs')
    voting_session = models.ForeignKey(VotingSession, on_delete=models.CASCADE, blank=True, null=True)
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, blank=True, null=True)
    
    # Audit Information
    action = models.CharField(max_length=30, choices=AUDIT_ACTIONS)
    description = models.TextField()
    
    # Network Information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # Additional Data
    metadata = models.JSONField(default=dict)
    
    # Timestamp
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'vote_audit_logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.voter.username}"


class VotingStatistics(models.Model):
    """
    Real-time voting statistics
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.OneToOneField('elections.Election', on_delete=models.CASCADE, related_name='voting_stats')
    
    # Vote Counts
    total_votes_cast = models.PositiveIntegerField(default=0)
    total_eligible_voters = models.PositiveIntegerField(default=0)
    votes_per_hour = models.JSONField(default=dict)  # Hourly vote counts
    
    # Blockchain Statistics
    votes_on_blockchain = models.PositiveIntegerField(default=0)
    pending_blockchain_votes = models.PositiveIntegerField(default=0)
    failed_blockchain_votes = models.PositiveIntegerField(default=0)
    
    # Performance Metrics
    average_voting_time = models.DurationField(blank=True, null=True)
    average_blockchain_confirmation_time = models.DurationField(blank=True, null=True)
    
    # Geographic Distribution
    votes_by_constituency = models.JSONField(default=dict)
    votes_by_polling_station = models.JSONField(default=dict)
    
    # Last Updated
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'voting_statistics'
    
    def __str__(self):
        return f"Voting stats for {self.election.title}"
    
    @property
    def turnout_percentage(self):
        if self.total_eligible_voters > 0:
            return (self.total_votes_cast / self.total_eligible_voters) * 100
        return 0
    
    @property
    def blockchain_success_rate(self):
        total_submitted = self.votes_on_blockchain + self.failed_blockchain_votes
        if total_submitted > 0:
            return (self.votes_on_blockchain / total_submitted) * 100
        return 0


class VoterReceipt(models.Model):
    """
    Digital receipt for voters
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vote = models.OneToOneField(Vote, on_delete=models.CASCADE, related_name='receipt')
    
    # Receipt Information
    receipt_number = models.CharField(max_length=20, unique=True)
    receipt_hash = models.CharField(max_length=64)
    
    # Vote Summary (encrypted)
    encrypted_vote_summary = models.TextField()
    
    # Verification Information
    verification_url = models.URLField(blank=True, null=True)
    qr_code_data = models.TextField(blank=True, null=True)
    
    # Timestamps
    issued_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'voter_receipts'
    
    def __str__(self):
        return f"Receipt {self.receipt_number} for {self.vote.voter.username}"
