"""
COMITIA Web Views for Authentication and User Management
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import User, CitizenProfile, VoterProfile, CandidateProfile
from .models import VoterOfficialProfile, ElectoralCommissionProfile


@csrf_protect
@never_cache
def login_view(request):
    """
    User login view
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                
                # Redirect to appropriate dashboard
                next_url = request.GET.get('next', 'accounts:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please provide both username and password.')
    
    return render(request, 'accounts/login.html', {
        'title': 'Login - COMITIA'
    })


@csrf_protect
def register_view(request):
    """
    User registration view
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password')
        password2 = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Basic validation
        if not all([username, email, password1, password2, first_name, last_name]):
            messages.error(request, 'All fields are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            try:
                with transaction.atomic():
                    # Create user
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password1,
                        first_name=first_name,
                        last_name=last_name,
                        user_type='citizen'  # Default to citizen
                    )
                    
                    # Create citizen profile
                    CitizenProfile.objects.get_or_create(user=user)
                    
                    # Log them in
                    login(request, user)
                    messages.success(request, f'Welcome to COMITIA, {user.get_full_name()}! Your account has been created successfully.')
                    
                    return redirect('accounts:dashboard')
                    
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, 'accounts/register.html', {
        'title': 'Register - COMITIA'
    })


@login_required
def logout_view(request):
    """
    User logout view
    """
    user_name = request.user.get_full_name() or request.user.username
    logout(request)
    messages.success(request, f'Goodbye, {user_name}! You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard_view(request):
    """
    Main dashboard view - routes to appropriate dashboard based on user type
    """
    user = request.user
    
    # Route to appropriate dashboard based on user type
    dashboard_routes = {
        'citizen': 'accounts:citizen_dashboard',
        'voter': 'accounts:voter_dashboard',
        'candidate': 'accounts:candidate_dashboard',
        'voter_official': 'accounts:voter_official_dashboard',
        'electoral_commission': 'accounts:electoral_commission_dashboard',
    }
    
    dashboard_route = dashboard_routes.get(user.user_type)
    if dashboard_route:
        return redirect(dashboard_route)
    else:
        # Default to citizen dashboard
        return redirect('accounts:citizen_dashboard')


@login_required
def profile_view(request):
    """
    User profile view
    """
    return render(request, 'accounts/profile.html', {
        'title': 'Profile - COMITIA',
        'user': request.user
    })


@login_required
def citizen_dashboard_view(request):
    """
    Citizen dashboard view
    """
    user = request.user
    
    # Get or create citizen profile
    try:
        citizen_profile = user.citizen_profile
    except:
        citizen_profile, created = CitizenProfile.objects.get_or_create(user=user)
    
    context = {
        'title': 'Citizen Dashboard - COMITIA',
        'user': user,
        'profile': citizen_profile,
        'dashboard_type': 'citizen',
        'can_apply_voter': user.user_type == 'citizen',
        'can_apply_candidate': user.user_type in ['citizen', 'voter'],
    }
    return render(request, 'dashboards/citizen_dashboard.html', context)


@login_required
def voter_dashboard_view(request):
    """
    Voter dashboard view
    """
    user = request.user
    
    # Get or create voter profile
    try:
        voter_profile = user.voter_profile
    except:
        voter_profile, created = VoterProfile.objects.get_or_create(user=user)
    
    # Mock data for elections (will be replaced with real data later)
    active_elections = []
    voting_history = []
    
    context = {
        'title': 'Voter Dashboard - COMITIA',
        'user': user,
        'profile': voter_profile,
        'dashboard_type': 'voter',
        'active_elections': active_elections,
        'voting_history': voting_history,
        'can_vote': user.can_vote,
        'verification_status': user.verification_status,
    }
    return render(request, 'dashboards/voter_dashboard.html', context)


@login_required
def candidate_dashboard_view(request):
    """
    Candidate dashboard view
    """
    user = request.user
    
    # Get or create candidate profile
    try:
        candidate_profile = user.candidate_profile
    except:
        candidate_profile, created = CandidateProfile.objects.get_or_create(user=user)
    
    # Mock data for campaigns (will be replaced with real data later)
    campaigns = []
    campaign_stats = {
        'total_supporters': 0,
        'total_donations': 0,
        'events_scheduled': 0,
        'social_media_reach': 0,
    }
    
    context = {
        'title': 'Candidate Dashboard - COMITIA',
        'user': user,
        'profile': candidate_profile,
        'dashboard_type': 'candidate',
        'campaigns': campaigns,
        'campaign_stats': campaign_stats,
        'verification_status': user.verification_status,
    }
    return render(request, 'dashboards/candidate_dashboard.html', context)


@login_required
def voter_official_dashboard_view(request):
    """
    Voter Official dashboard view
    """
    user = request.user
    
    if not user.is_voter_official:
        messages.error(request, 'Access denied. Voter Official privileges required.')
        return redirect('accounts:dashboard')
    
    # Get or create voter official profile
    try:
        official_profile = user.voter_official_profile
    except:
        official_profile, created = VoterOfficialProfile.objects.get_or_create(user=user)
    
    # Mock data for pending registrations (will be replaced with real data later)
    pending_registrations = []
    registration_stats = {
        'pending_count': 0,
        'approved_today': 0,
        'rejected_today': 0,
        'total_processed': 0,
    }
    
    context = {
        'title': 'Voter Official Dashboard - COMITIA',
        'user': user,
        'profile': official_profile,
        'dashboard_type': 'voter_official',
        'pending_registrations': pending_registrations,
        'registration_stats': registration_stats,
    }
    return render(request, 'dashboards/voter_official_dashboard.html', context)


@login_required
def electoral_commission_dashboard_view(request):
    """
    Electoral Commission dashboard view
    """
    user = request.user
    
    if not user.is_electoral_commission:
        messages.error(request, 'Access denied. Electoral Commission privileges required.')
        return redirect('accounts:dashboard')
    
    # Get or create electoral commission profile
    try:
        commission_profile = user.electoral_commission_profile
    except:
        commission_profile, created = ElectoralCommissionProfile.objects.get_or_create(user=user)
    
    # Mock data for system overview (will be replaced with real data later)
    system_stats = {
        'total_elections': 0,
        'active_elections': 0,
        'total_voters': 0,
        'pending_candidates': 0,
        'total_votes_cast': 0,
    }
    
    recent_activities = []
    
    context = {
        'title': 'Electoral Commission Dashboard - COMITIA',
        'user': user,
        'profile': commission_profile,
        'dashboard_type': 'electoral_commission',
        'system_stats': system_stats,
        'recent_activities': recent_activities,
    }
    return render(request, 'dashboards/electoral_commission_dashboard.html', context)


@login_required
def role_transition_view(request):
    """
    Handle user role transitions (e.g., citizen to voter, citizen to candidate)
    """
    user = request.user
    
    if request.method == 'POST':
        new_role = request.POST.get('new_role')
        
        if new_role == 'voter' and user.user_type == 'citizen':
            # Transition from citizen to voter (requires approval)
            messages.info(request, 'Voter registration application submitted. Please visit a Voter Official for biometric verification.')
        elif new_role == 'candidate' and user.user_type in ['citizen', 'voter']:
            # Transition to candidate (requires approval)
            messages.info(request, 'Candidate application submitted. Awaiting Electoral Commission approval.')
        else:
            messages.error(request, 'Invalid role transition requested.')
    
    context = {
        'title': 'Role Transition - COMITIA',
        'user': request.user,
        'available_roles': get_available_role_transitions(user)
    }
    return render(request, 'accounts/role_transition.html', context)


def get_available_role_transitions(user):
    """
    Get available role transitions for a user
    """
    transitions = []
    
    if user.user_type == 'citizen':
        transitions.extend([
            {'role': 'voter', 'name': 'Voter', 'description': 'Apply for voter registration'},
            {'role': 'candidate', 'name': 'Candidate', 'description': 'Apply to run for office'}
        ])
    elif user.user_type == 'voter':
        transitions.append({
            'role': 'candidate', 
            'name': 'Candidate', 
            'description': 'Apply to run for office'
        })
    
    return transitions

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # If you want to allow unauthenticated AJAX, else use @csrf_protect
@require_POST
def check_username_view(request):
    import json
    try:
        data = json.loads(request.body.decode())
        username = data.get('username', '').strip()
        available = not User.objects.filter(username=username).exists() if username else False
        return JsonResponse({'available': available})
    except Exception:
        return JsonResponse({'available': False}, status=400)


def password_reset_view(request):
    """
    Password reset view (placeholder for now)
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # TODO: Implement actual password reset email functionality
            messages.success(request, 'If an account with that email exists, we have sent you a password reset link.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please enter a valid email address.')
    
    return render(request, 'accounts/password_reset.html', {
        'title': 'Password Reset - COMITIA'
    })

