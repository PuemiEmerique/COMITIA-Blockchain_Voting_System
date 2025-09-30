"""
COMITIA Elections URLs
Election management endpoints
"""

from django.urls import path
from . import views

urlpatterns = [
    # Election Management
    path('', views.ElectionListView.as_view(), name='election-list'),
    path('create/', views.ElectionCreateView.as_view(), name='election-create'),
    path('my-elections/', views.MyElectionsView.as_view(), name='my-elections'),
    path('statistics/', views.election_statistics, name='election-statistics'),
    
    # Election Details
    path('<uuid:pk>/', views.ElectionDetailView.as_view(), name='election-detail'),
    path('<uuid:pk>/update/', views.ElectionUpdateView.as_view(), name='election-update'),
    
    # Candidate Management
    path('<uuid:election_id>/candidates/', views.ElectionCandidatesView.as_view(), name='election-candidates'),
    path('<uuid:election_id>/register-candidate/', views.register_candidate, name='register-candidate'),
    path('pending-candidates/', views.PendingCandidatesView.as_view(), name='pending-candidates'),
    path('candidates/<uuid:candidate_id>/approve/', views.approve_candidate, name='approve-candidate'),
    path('candidates/<uuid:candidate_id>/reject/', views.reject_candidate, name='reject-candidate'),
    
    # Voting
    path('<uuid:election_id>/ballot/', views.get_ballot, name='get-ballot'),
    path('<uuid:election_id>/eligibility/', views.check_voter_eligibility, name='check-voter-eligibility'),
    
    # Results
    path('<uuid:election_id>/results/', views.ElectionResultsView.as_view(), name='election-results'),
    path('<uuid:election_id>/publish-results/', views.publish_results, name='publish-results'),
]
