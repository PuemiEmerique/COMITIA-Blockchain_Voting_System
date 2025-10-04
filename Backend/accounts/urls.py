"""
COMITIA Accounts URLs
Authentication and user management endpoints
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views, web_views

app_name = 'accounts'

urlpatterns = [
    # Web Authentication Views
    path('login/', web_views.login_view, name='login'),
    path('role-login/', web_views.role_login_view, name='role_login'),
    path('register/', web_views.register_view, name='register'),
    path('logout/', web_views.logout_view, name='logout'),
    path('profile/', web_views.profile_view, name='profile'),
    path('check-username/', web_views.check_username_view, name='check_username'),
    path('password-reset/', web_views.password_reset_view, name='password_reset'),
    
    # Dashboard Views
    path('dashboard/', web_views.dashboard_view, name='dashboard'),
    path('dashboard/superadmin/', web_views.superadmin_dashboard_view, name='superadmin_dashboard'),
    path('dashboard/citizen/', web_views.citizen_dashboard_view, name='citizen_dashboard'),
    path('dashboard/voter/', web_views.voter_dashboard_view, name='voter_dashboard'),
    path('dashboard/candidate/', web_views.candidate_dashboard_view, name='candidate_dashboard'),
    path('dashboard/voter-official/', web_views.voter_official_dashboard_view, name='voter_official_dashboard'),
    path('dashboard/electoral-commission/', web_views.electoral_commission_dashboard_view, name='electoral_commission_dashboard'),
    
    # Role Transitions
    path('role-transition/', web_views.role_transition_view, name='role_transition'),
    
    # API Authentication (for future use)
    path('api/register/', views.UserRegistrationView.as_view(), name='api-user-register'),
    path('api/login/', views.login_view, name='api-user-login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
    
    # API User Profile (for future use)
    path('api/profile/', views.UserProfileView.as_view(), name='api-user-profile'),
    path('api/dashboard/', views.user_dashboard, name='api-user-dashboard'),
    path('api/change-password/', views.change_password, name='api-change-password'),
    
    # API Citizen Features (for future use)
    path('api/citizen/profile/', views.CitizenProfileView.as_view(), name='api-citizen-profile'),
    path('api/citizen/voter-pre-enrollment/', views.voter_pre_enrollment, name='api-voter-pre-enrollment'),
    path('api/citizen/candidate-application/', views.candidate_application, name='api-candidate-application'),
    
    # API Voter Official Features (for future use)
    path('api/voter-official/pending-enrollments/', views.PendingVoterEnrollmentsView.as_view(), name='api-pending-voter-enrollments'),
    path('api/voter-official/approve-enrollment/<uuid:user_id>/', views.approve_voter_enrollment, name='api-approve-voter-enrollment'),
    
    # API Electoral Commission Features (for future use)
    path('api/electoral-commission/pending-candidates/', views.PendingCandidateApplicationsView.as_view(), name='api-pending-candidate-applications'),
    path('api/electoral-commission/approve-candidate/<str:candidate_id>/', views.approve_candidate_application, name='api-approve-candidate-application'),
]
