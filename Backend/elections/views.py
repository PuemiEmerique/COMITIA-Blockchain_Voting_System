"""
COMITIA Elections Views
Handle election management and candidate registration
"""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.db.models import Count, Q

from .models import (
    Election, ElectionPosition, ElectionCandidate, ElectionConstituency,
    PollingStation, ElectionResult, ElectionAuditLog
)
from .serializers import (
    ElectionSerializer, ElectionDetailSerializer, ElectionCreateSerializer,
    ElectionPositionSerializer, ElectionCandidateSerializer,
    CandidateRegistrationSerializer, ElectionResultSerializer,
    ElectionStatsSerializer, VoterEligibilitySerializer, BallotSerializer
)
from accounts.permissions import (
    IsElectoralCommission, IsCandidate, CanVote, IsApprovedUser
)
from accounts.models import User, UserActivity


class ElectionListView(generics.ListAPIView):
    """
    List all elections (public endpoint)
    """
    serializer_class = ElectionSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Election.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by election type
        type_filter = self.request.query_params.get('type')
        if type_filter:
            queryset = queryset.filter(election_type=type_filter)
        
        # Filter by active elections (registration or voting open)
        if self.request.query_params.get('active') == 'true':
            now = timezone.now()
            queryset = queryset.filter(
                Q(registration_start_date__lte=now, registration_end_date__gte=now) |
                Q(voting_start_date__lte=now, voting_end_date__gte=now)
            )
        
        return queryset.order_by('-created_at')


class ElectionDetailView(generics.RetrieveAPIView):
    """
    Get detailed election information
    """
    queryset = Election.objects.all()
    serializer_class = ElectionDetailSerializer
    permission_classes = [permissions.AllowAny]


class ElectionCreateView(generics.CreateAPIView):
    """
    Create new election (Electoral Commission only)
    """
    serializer_class = ElectionCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsElectoralCommission]
    
    def perform_create(self, serializer):
        with transaction.atomic():
            election = serializer.save(created_by=self.request.user)
            
            # Log election creation
            ElectionAuditLog.objects.create(
                election=election,
                action='election_created',
                description=f'Election "{election.title}" created',
                performed_by=self.request.user,
                ip_address=self.request.META.get('REMOTE_ADDR'),
                user_agent=self.request.META.get('HTTP_USER_AGENT')
            )
            
            # Log user activity
            UserActivity.objects.create(
                user=self.request.user,
                activity_type='election_created',
                description=f'Created election: {election.title}',
                ip_address=self.request.META.get('REMOTE_ADDR'),
                user_agent=self.request.META.get('HTTP_USER_AGENT'),
                metadata={'election_id': str(election.id)}
            )


class ElectionUpdateView(generics.UpdateAPIView):
    """
    Update election (Electoral Commission only)
    """
    queryset = Election.objects.all()
    serializer_class = ElectionSerializer
    permission_classes = [permissions.IsAuthenticated, IsElectoralCommission]
    
    def perform_update(self, serializer):
        with transaction.atomic():
            election = serializer.save()
            
            # Log election update
            ElectionAuditLog.objects.create(
                election=election,
                action='election_updated',
                description=f'Election "{election.title}" updated',
                performed_by=self.request.user,
                ip_address=self.request.META.get('REMOTE_ADDR'),
                user_agent=self.request.META.get('HTTP_USER_AGENT')
            )


class ElectionCandidatesView(generics.ListAPIView):
    """
    List candidates for a specific election
    """
    serializer_class = ElectionCandidateSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        election_id = self.kwargs['election_id']
        queryset = ElectionCandidate.objects.filter(election_id=election_id)
        
        # Filter by position
        position_id = self.request.query_params.get('position')
        if position_id:
            queryset = queryset.filter(position_id=position_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', 'approved')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.select_related('candidate', 'position').order_by('ballot_number')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def register_candidate(request, election_id):
    """
    Register as candidate for an election
    """
    try:
        election = Election.objects.get(id=election_id)
    except Election.DoesNotExist:
        return Response({
            'error': 'Election not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user can apply for candidacy
    if request.user.user_type not in ['citizen', 'voter']:
        return Response({
            'error': 'Only citizens and voters can apply for candidacy'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Check if registration is open
    if not election.is_registration_open:
        return Response({
            'error': 'Registration is not open for this election'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = CandidateRegistrationSerializer(
        data=request.data,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    
    with transaction.atomic():
        # Check if user is already registered for this position
        position = serializer.validated_data['position']
        existing_registration = ElectionCandidate.objects.filter(
            election=election,
            position=position,
            candidate=request.user
        ).first()
        
        if existing_registration:
            return Response({
                'error': 'You are already registered for this position'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create candidate registration
        candidate_registration = serializer.save()
        
        # Update user type to candidate if not already
        if request.user.user_type != 'candidate':
            request.user.user_type = 'candidate'
            request.user.save()
        
        # Log candidate registration
        ElectionAuditLog.objects.create(
            election=election,
            action='candidate_registered',
            description=f'{request.user.get_full_name()} registered for {position.title}',
            performed_by=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={
                'candidate_id': str(request.user.id),
                'position_id': str(position.id)
            }
        )
        
        # Log user activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='candidate_registered',
            description=f'Registered as candidate for {position.title} in {election.title}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'election_id': str(election.id), 'position_id': str(position.id)}
        )
    
    return Response({
        'message': 'Candidate registration submitted successfully',
        'registration': ElectionCandidateSerializer(candidate_registration).data
    }, status=status.HTTP_201_CREATED)


class PendingCandidatesView(generics.ListAPIView):
    """
    List pending candidate registrations (Electoral Commission only)
    """
    serializer_class = ElectionCandidateSerializer
    permission_classes = [permissions.IsAuthenticated, IsElectoralCommission]
    
    def get_queryset(self):
        return ElectionCandidate.objects.filter(
            status='registered'
        ).select_related('candidate', 'position', 'election').order_by('-registration_date')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsElectoralCommission])
def approve_candidate(request, candidate_id):
    """
    Approve candidate registration (Electoral Commission only)
    """
    try:
        candidate_registration = ElectionCandidate.objects.get(id=candidate_id)
    except ElectionCandidate.DoesNotExist:
        return Response({
            'error': 'Candidate registration not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if candidate_registration.status != 'registered':
        return Response({
            'error': 'This candidate registration is not pending approval'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    with transaction.atomic():
        # Update candidate status
        candidate_registration.status = 'approved'
        candidate_registration.approved_by = request.user
        candidate_registration.approved_at = timezone.now()
        
        # Assign ballot number
        max_ballot_number = ElectionCandidate.objects.filter(
            election=candidate_registration.election,
            position=candidate_registration.position,
            status='approved'
        ).aggregate(max_number=models.Max('ballot_number'))['max_number'] or 0
        
        candidate_registration.ballot_number = max_ballot_number + 1
        candidate_registration.save()
        
        # Update candidate user verification status
        candidate_registration.candidate.verification_status = 'approved'
        candidate_registration.candidate.save()
        
        # Log approval
        ElectionAuditLog.objects.create(
            election=candidate_registration.election,
            action='candidate_approved',
            description=f'Approved {candidate_registration.candidate.get_full_name()} for {candidate_registration.position.title}',
            performed_by=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'candidate_id': str(candidate_registration.candidate.id)}
        )
    
    return Response({
        'message': 'Candidate approved successfully',
        'candidate': ElectionCandidateSerializer(candidate_registration).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsElectoralCommission])
def reject_candidate(request, candidate_id):
    """
    Reject candidate registration (Electoral Commission only)
    """
    try:
        candidate_registration = ElectionCandidate.objects.get(id=candidate_id)
    except ElectionCandidate.DoesNotExist:
        return Response({
            'error': 'Candidate registration not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    reason = request.data.get('reason', 'No reason provided')
    
    with transaction.atomic():
        # Update candidate status
        candidate_registration.status = 'rejected'
        candidate_registration.save()
        
        # Log rejection
        ElectionAuditLog.objects.create(
            election=candidate_registration.election,
            action='candidate_rejected',
            description=f'Rejected {candidate_registration.candidate.get_full_name()} for {candidate_registration.position.title}. Reason: {reason}',
            performed_by=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={
                'candidate_id': str(candidate_registration.candidate.id),
                'reason': reason
            }
        )
    
    return Response({
        'message': 'Candidate rejected successfully'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, CanVote])
def get_ballot(request, election_id):
    """
    Get ballot for voting (Voters and Candidates only)
    """
    try:
        election = Election.objects.get(id=election_id)
    except Election.DoesNotExist:
        return Response({
            'error': 'Election not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if voting is open
    if not election.is_voting_open:
        return Response({
            'error': 'Voting is not open for this election'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user has already voted (will be implemented in voting app)
    # For now, just return the ballot
    
    serializer = BallotSerializer(election, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_voter_eligibility(request, election_id):
    """
    Check if user is eligible to vote in an election
    """
    try:
        election = Election.objects.get(id=election_id)
    except Election.DoesNotExist:
        return Response({
            'error': 'Election not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    is_eligible = True
    reasons = []
    
    # Check if user can vote
    if not user.can_vote:
        is_eligible = False
        reasons.append('User is not registered as a voter')
    
    # Check if user is approved
    if user.verification_status != 'approved':
        is_eligible = False
        reasons.append('User account is not approved')
    
    # Check if biometric registration is required and completed
    if election.require_biometric_auth and not user.is_biometric_registered:
        is_eligible = False
        reasons.append('Biometric registration required')
    
    # Check if voting is open
    if not election.is_voting_open:
        is_eligible = False
        reasons.append('Voting is not currently open')
    
    # Get assigned polling station (if applicable)
    assigned_polling_station = None
    if hasattr(user, 'voter_profile') and user.voter_profile.polling_station:
        try:
            assigned_polling_station = PollingStation.objects.get(
                name=user.voter_profile.polling_station
            )
        except PollingStation.DoesNotExist:
            pass
    
    return Response({
        'election_id': election_id,
        'is_eligible': is_eligible,
        'eligibility_reasons': reasons,
        'assigned_polling_station': PollingStationSerializer(assigned_polling_station).data if assigned_polling_station else None
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsElectoralCommission])
def election_statistics(request):
    """
    Get election statistics (Electoral Commission only)
    """
    stats = {
        'total_elections': Election.objects.count(),
        'active_elections': Election.objects.filter(
            status__in=['scheduled', 'active']
        ).count(),
        'completed_elections': Election.objects.filter(status='completed').count(),
        'total_candidates': ElectionCandidate.objects.filter(status='approved').count(),
        'total_voters': User.objects.filter(user_type='voter').count(),
        'total_votes_cast': Election.objects.aggregate(
            total=models.Sum('total_votes_cast')
        )['total'] or 0,
        'average_turnout': Election.objects.filter(
            status='completed'
        ).aggregate(
            avg_turnout=models.Avg('voter_turnout_percentage')
        )['avg_turnout'] or 0
    }
    
    serializer = ElectionStatsSerializer(stats)
    return Response(serializer.data)


class ElectionResultsView(generics.ListAPIView):
    """
    Get election results
    """
    serializer_class = ElectionResultSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        election_id = self.kwargs['election_id']
        return ElectionResult.objects.filter(
            election_id=election_id
        ).select_related('candidate__candidate', 'position').order_by('position', 'rank')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsElectoralCommission])
def publish_results(request, election_id):
    """
    Publish election results (Electoral Commission only)
    """
    try:
        election = Election.objects.get(id=election_id)
    except Election.DoesNotExist:
        return Response({
            'error': 'Election not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if election.results_published:
        return Response({
            'error': 'Results are already published'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    with transaction.atomic():
        # Mark results as published
        election.results_published = True
        election.results_published_at = timezone.now()
        election.status = 'completed'
        election.save()
        
        # Update all results publication timestamp
        ElectionResult.objects.filter(election=election).update(
            published_at=timezone.now()
        )
        
        # Log results publication
        ElectionAuditLog.objects.create(
            election=election,
            action='results_published',
            description=f'Results published for {election.title}',
            performed_by=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
    
    return Response({
        'message': 'Election results published successfully'
    })


class MyElectionsView(generics.ListAPIView):
    """
    Get elections relevant to the current user
    """
    serializer_class = ElectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_electoral_commission:
            # Electoral Commission sees all elections
            return Election.objects.all().order_by('-created_at')
        elif user.is_candidate:
            # Candidates see elections they're registered for
            candidate_elections = ElectionCandidate.objects.filter(
                candidate=user
            ).values_list('election_id', flat=True)
            return Election.objects.filter(id__in=candidate_elections).order_by('-created_at')
        else:
            # Voters and citizens see active elections
            now = timezone.now()
            return Election.objects.filter(
                Q(registration_start_date__lte=now, registration_end_date__gte=now) |
                Q(voting_start_date__lte=now, voting_end_date__gte=now) |
                Q(status='completed', results_published=True)
            ).order_by('-created_at')
