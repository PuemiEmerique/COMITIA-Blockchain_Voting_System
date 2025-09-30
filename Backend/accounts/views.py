"""
COMITIA Authentication and User Management Views
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.utils import timezone
from django.db import transaction

from .models import (
    User, CitizenProfile, VoterProfile, CandidateProfile,
    VoterOfficialProfile, ElectoralCommissionProfile, UserActivity
)
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    CitizenProfileSerializer, VoterProfileSerializer, CandidateProfileSerializer,
    CandidateApplicationSerializer, VoterPreEnrollmentSerializer,
    UserRoleTransitionSerializer, PasswordChangeSerializer
)
from .permissions import IsElectoralCommission, IsVoterOfficial, IsOwnerOrReadOnly


class UserRegistrationView(generics.CreateAPIView):
    """
    Register new users (Citizens by default)
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            user = serializer.save()
            
            # Log registration activity
            UserActivity.objects.create(
                user=user,
                activity_type='registration',
                description='User registered as citizen',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Registration successful',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    User login endpoint
    """
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.validated_data['user']
    login(request, user)
    
    # Update last activity
    user.last_activity = timezone.now()
    user.save()
    
    # Log login activity
    UserActivity.objects.create(
        user=user,
        activity_type='login',
        description='User logged in',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT')
    )
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'Login successful',
        'user': UserProfileSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        
        # Log profile update activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='profile_update',
            description='User updated profile',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        return response


class CitizenProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update citizen profile
    """
    serializer_class = CitizenProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        citizen_profile, created = CitizenProfile.objects.get_or_create(
            user=self.request.user
        )
        return citizen_profile


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def voter_pre_enrollment(request):
    """
    Citizen applies for voter pre-enrollment
    """
    if not request.user.is_citizen:
        return Response({
            'error': 'Only citizens can apply for voter enrollment'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = VoterPreEnrollmentSerializer(
        instance=request.user, 
        data=request.data
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    # Log pre-enrollment activity
    UserActivity.objects.create(
        user=request.user,
        activity_type='voter_pre_enrollment',
        description='Citizen applied for voter pre-enrollment',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT')
    )
    
    return Response({
        'message': 'Voter pre-enrollment application submitted successfully'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def candidate_application(request):
    """
    Citizen/Voter applies for candidacy
    """
    if request.user.user_type not in ['citizen', 'voter']:
        return Response({
            'error': 'Only citizens and voters can apply for candidacy'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Check if user already has a candidate profile
    if hasattr(request.user, 'candidate_profile'):
        return Response({
            'error': 'You have already applied for candidacy'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = CandidateApplicationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    with transaction.atomic():
        # Create candidate profile
        candidate_profile = CandidateProfile.objects.create(
            user=request.user,
            candidate_id=f"CAND_{request.user.id.hex[:8].upper()}",
            **serializer.validated_data
        )
        
        # Update user type to candidate
        request.user.user_type = 'candidate'
        request.user.save()
        
        # Log candidacy application
        UserActivity.objects.create(
            user=request.user,
            activity_type='candidate_application',
            description='User applied for candidacy',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
    
    return Response({
        'message': 'Candidacy application submitted successfully',
        'candidate_profile': CandidateProfileSerializer(candidate_profile).data
    })


class PendingVoterEnrollmentsView(generics.ListAPIView):
    """
    List pending voter enrollments (for Voter Officials)
    """
    serializer_class = CitizenProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsVoterOfficial]
    
    def get_queryset(self):
        return CitizenProfile.objects.filter(
            voter_pre_enrollment_status='pending'
        ).select_related('user')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsVoterOfficial])
def approve_voter_enrollment(request, user_id):
    """
    Approve voter enrollment (Voter Officials only)
    """
    try:
        user = User.objects.get(id=user_id)
        citizen_profile = user.citizen_profile
        
        if citizen_profile.voter_pre_enrollment_status != 'pending':
            return Response({
                'error': 'This enrollment is not pending approval'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Update citizen profile
            citizen_profile.voter_pre_enrollment_status = 'approved'
            citizen_profile.save()
            
            # Create voter profile
            voter_profile = VoterProfile.objects.create(
                user=user,
                voter_id=f"VOTER_{user.id.hex[:8].upper()}",
                registration_completed_by=request.user
            )
            
            # Update user type to voter
            user.user_type = 'voter'
            user.verification_status = 'approved'
            user.save()
            
            # Log approval activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='voter_approved',
                description=f'Approved voter enrollment for {user.get_full_name()}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                metadata={'approved_user_id': str(user.id)}
            )
        
        return Response({
            'message': 'Voter enrollment approved successfully',
            'voter_profile': VoterProfileSerializer(voter_profile).data
        })
        
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)


class PendingCandidateApplicationsView(generics.ListAPIView):
    """
    List pending candidate applications (for Electoral Commission)
    """
    serializer_class = CandidateProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsElectoralCommission]
    
    def get_queryset(self):
        return CandidateProfile.objects.filter(
            application_status='pending'
        ).select_related('user')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsElectoralCommission])
def approve_candidate_application(request, candidate_id):
    """
    Approve candidate application (Electoral Commission only)
    """
    try:
        candidate_profile = CandidateProfile.objects.get(candidate_id=candidate_id)
        
        if candidate_profile.application_status != 'pending':
            return Response({
                'error': 'This application is not pending approval'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Update candidate profile
            candidate_profile.application_status = 'approved'
            candidate_profile.approved_by = request.user
            candidate_profile.save()
            
            # Update user verification status
            candidate_profile.user.verification_status = 'approved'
            candidate_profile.user.save()
            
            # Log approval activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='candidate_approved',
                description=f'Approved candidate application for {candidate_profile.user.get_full_name()}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                metadata={'candidate_id': candidate_id}
            )
        
        return Response({
            'message': 'Candidate application approved successfully',
            'candidate_profile': CandidateProfileSerializer(candidate_profile).data
        })
        
    except CandidateProfile.DoesNotExist:
        return Response({
            'error': 'Candidate not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """
    Change user password
    """
    serializer = PasswordChangeSerializer(
        data=request.data, 
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    
    # Change password
    request.user.set_password(serializer.validated_data['new_password'])
    request.user.save()
    
    # Log password change activity
    UserActivity.objects.create(
        user=request.user,
        activity_type='password_change',
        description='User changed password',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT')
    )
    
    return Response({
        'message': 'Password changed successfully'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard(request):
    """
    Get user dashboard data based on user type
    """
    user = request.user
    dashboard_data = {
        'user': UserProfileSerializer(user).data,
        'user_type': user.user_type,
        'can_vote': user.can_vote,
        'can_manage_elections': user.can_manage_elections,
        'can_manage_voters': user.can_manage_voters,
    }
    
    # Add role-specific data
    if user.is_citizen and hasattr(user, 'citizen_profile'):
        dashboard_data['citizen_profile'] = CitizenProfileSerializer(user.citizen_profile).data
    
    if user.is_voter and hasattr(user, 'voter_profile'):
        dashboard_data['voter_profile'] = VoterProfileSerializer(user.voter_profile).data
    
    if user.is_candidate and hasattr(user, 'candidate_profile'):
        dashboard_data['candidate_profile'] = CandidateProfileSerializer(user.candidate_profile).data
    
    if user.is_voter_official and hasattr(user, 'voter_official_profile'):
        dashboard_data['voter_official_profile'] = VoterOfficialProfileSerializer(user.voter_official_profile).data
        dashboard_data['pending_enrollments_count'] = CitizenProfile.objects.filter(
            voter_pre_enrollment_status='pending'
        ).count()
    
    if user.is_electoral_commission and hasattr(user, 'electoral_commission_profile'):
        dashboard_data['electoral_commission_profile'] = ElectoralCommissionProfileSerializer(user.electoral_commission_profile).data
        dashboard_data['pending_candidates_count'] = CandidateProfile.objects.filter(
            application_status='pending'
        ).count()
    
    return Response(dashboard_data)
