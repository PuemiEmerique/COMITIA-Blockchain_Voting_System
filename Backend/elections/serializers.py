"""
COMITIA Elections Serializers
Handle serialization for election management
"""

from rest_framework import serializers
from django.utils import timezone
from .models import (
    Election, ElectionPosition, ElectionCandidate, ElectionConstituency,
    PollingStation, ElectionResult, ElectionAuditLog
)
from accounts.serializers import UserProfileSerializer


class ElectionPositionSerializer(serializers.ModelSerializer):
    """
    Serializer for election positions
    """
    candidates_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ElectionPosition
        fields = [
            'id', 'title', 'description', 'max_votes_per_voter',
            'available_seats', 'minimum_age', 'citizenship_required',
            'display_order', 'is_active', 'candidates_count'
        ]
    
    def get_candidates_count(self, obj):
        return obj.candidates.filter(status='approved').count()


class ElectionCandidateSerializer(serializers.ModelSerializer):
    """
    Serializer for election candidates
    """
    candidate_info = UserProfileSerializer(source='candidate', read_only=True)
    position_title = serializers.CharField(source='position.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = ElectionCandidate
        fields = [
            'id', 'candidate_info', 'position_title', 'registration_date',
            'status', 'status_display', 'campaign_name', 'campaign_slogan',
            'campaign_logo', 'ballot_number', 'ballot_symbol',
            'total_votes', 'vote_percentage', 'approved_by_name', 'approved_at'
        ]
        read_only_fields = [
            'registration_date', 'total_votes', 'vote_percentage',
            'approved_by_name', 'approved_at'
        ]


class ElectionConstituencySerializer(serializers.ModelSerializer):
    """
    Serializer for election constituencies
    """
    polling_stations_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ElectionConstituency
        fields = [
            'id', 'name', 'code', 'description', 'region',
            'state_province', 'registered_voters_count', 'polling_stations_count'
        ]
    
    def get_polling_stations_count(self, obj):
        return obj.polling_stations.filter(is_active=True).count()


class PollingStationSerializer(serializers.ModelSerializer):
    """
    Serializer for polling stations
    """
    constituency_name = serializers.CharField(source='constituency.name', read_only=True)
    presiding_officer_name = serializers.CharField(source='presiding_officer.get_full_name', read_only=True)
    
    class Meta:
        model = PollingStation
        fields = [
            'id', 'name', 'code', 'address', 'latitude', 'longitude',
            'capacity', 'assigned_voters_count', 'constituency_name',
            'presiding_officer_name', 'is_active'
        ]


class ElectionSerializer(serializers.ModelSerializer):
    """
    Serializer for elections
    """
    election_type_display = serializers.CharField(source='get_election_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    positions_count = serializers.SerializerMethodField()
    candidates_count = serializers.SerializerMethodField()
    is_registration_open = serializers.ReadOnlyField()
    is_voting_open = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    voter_turnout_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Election
        fields = [
            'id', 'title', 'description', 'election_type', 'election_type_display',
            'status', 'status_display', 'registration_start_date', 'registration_end_date',
            'voting_start_date', 'voting_end_date', 'max_candidates_per_position',
            'allow_multiple_votes', 'require_biometric_auth', 'blockchain_contract_address',
            'blockchain_network', 'created_by_name', 'created_at', 'updated_at',
            'total_votes_cast', 'total_eligible_voters', 'results_published',
            'results_published_at', 'positions_count', 'candidates_count',
            'is_registration_open', 'is_voting_open', 'is_completed', 'voter_turnout_percentage'
        ]
        read_only_fields = [
            'created_by_name', 'created_at', 'updated_at', 'total_votes_cast',
            'total_eligible_voters', 'results_published', 'results_published_at'
        ]
    
    def get_positions_count(self, obj):
        return obj.positions.filter(is_active=True).count()
    
    def get_candidates_count(self, obj):
        return ElectionCandidate.objects.filter(
            election=obj, 
            status='approved'
        ).count()
    
    def validate(self, attrs):
        """
        Validate election dates
        """
        reg_start = attrs.get('registration_start_date')
        reg_end = attrs.get('registration_end_date')
        vote_start = attrs.get('voting_start_date')
        vote_end = attrs.get('voting_end_date')
        
        if reg_start and reg_end and reg_start >= reg_end:
            raise serializers.ValidationError(
                "Registration end date must be after start date"
            )
        
        if vote_start and vote_end and vote_start >= vote_end:
            raise serializers.ValidationError(
                "Voting end date must be after start date"
            )
        
        if reg_end and vote_start and reg_end > vote_start:
            raise serializers.ValidationError(
                "Voting cannot start before registration ends"
            )
        
        return attrs


class ElectionDetailSerializer(ElectionSerializer):
    """
    Detailed serializer for elections with related data
    """
    positions = ElectionPositionSerializer(many=True, read_only=True)
    constituencies = ElectionConstituencySerializer(many=True, read_only=True)
    
    class Meta(ElectionSerializer.Meta):
        fields = ElectionSerializer.Meta.fields + ['positions', 'constituencies']


class ElectionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating elections
    """
    positions = ElectionPositionSerializer(many=True, write_only=True)
    
    class Meta:
        model = Election
        fields = [
            'title', 'description', 'election_type', 'registration_start_date',
            'registration_end_date', 'voting_start_date', 'voting_end_date',
            'max_candidates_per_position', 'allow_multiple_votes',
            'require_biometric_auth', 'blockchain_network', 'positions'
        ]
    
    def create(self, validated_data):
        positions_data = validated_data.pop('positions')
        election = Election.objects.create(**validated_data)
        
        # Create positions
        for position_data in positions_data:
            ElectionPosition.objects.create(election=election, **position_data)
        
        return election


class CandidateRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for candidate registration
    """
    class Meta:
        model = ElectionCandidate
        fields = [
            'position', 'campaign_name', 'campaign_slogan', 'campaign_logo'
        ]
    
    def validate_position(self, value):
        """
        Validate that the position belongs to an election with open registration
        """
        if not value.election.is_registration_open:
            raise serializers.ValidationError(
                "Registration is not open for this election"
            )
        return value
    
    def create(self, validated_data):
        # Add the candidate (current user) to the validated data
        validated_data['candidate'] = self.context['request'].user
        validated_data['election'] = validated_data['position'].election
        return super().create(validated_data)


class ElectionResultSerializer(serializers.ModelSerializer):
    """
    Serializer for election results
    """
    candidate_name = serializers.CharField(source='candidate.candidate.get_full_name', read_only=True)
    position_title = serializers.CharField(source='position.title', read_only=True)
    
    class Meta:
        model = ElectionResult
        fields = [
            'id', 'candidate_name', 'position_title', 'total_votes',
            'vote_percentage', 'rank', 'is_winner', 'blockchain_hash',
            'is_verified', 'calculated_at', 'published_at'
        ]


class ElectionAuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for election audit logs
    """
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    
    class Meta:
        model = ElectionAuditLog
        fields = [
            'id', 'action', 'action_display', 'description',
            'performed_by_name', 'ip_address', 'metadata', 'timestamp'
        ]


class ElectionStatsSerializer(serializers.Serializer):
    """
    Serializer for election statistics
    """
    total_elections = serializers.IntegerField()
    active_elections = serializers.IntegerField()
    completed_elections = serializers.IntegerField()
    total_candidates = serializers.IntegerField()
    total_voters = serializers.IntegerField()
    total_votes_cast = serializers.IntegerField()
    average_turnout = serializers.DecimalField(max_digits=5, decimal_places=2)


class VoterEligibilitySerializer(serializers.Serializer):
    """
    Serializer for checking voter eligibility
    """
    election_id = serializers.UUIDField()
    is_eligible = serializers.BooleanField(read_only=True)
    eligibility_reasons = serializers.ListField(
        child=serializers.CharField(), 
        read_only=True
    )
    assigned_polling_station = PollingStationSerializer(read_only=True)


class BallotSerializer(serializers.Serializer):
    """
    Serializer for election ballot
    """
    election = ElectionSerializer(read_only=True)
    positions = serializers.SerializerMethodField()
    voter_info = serializers.SerializerMethodField()
    
    def get_positions(self, obj):
        """
        Get positions with their candidates for the ballot
        """
        positions = obj.positions.filter(is_active=True).order_by('display_order')
        ballot_positions = []
        
        for position in positions:
            candidates = position.candidates.filter(status='approved').order_by('ballot_number')
            ballot_positions.append({
                'id': position.id,
                'title': position.title,
                'description': position.description,
                'max_votes_per_voter': position.max_votes_per_voter,
                'candidates': ElectionCandidateSerializer(candidates, many=True).data
            })
        
        return ballot_positions
    
    def get_voter_info(self, obj):
        """
        Get voter information for the ballot
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            if hasattr(user, 'voter_profile'):
                return {
                    'voter_id': user.voter_profile.voter_id,
                    'polling_station': user.voter_profile.polling_station,
                    'constituency': user.voter_profile.constituency
                }
        return None
