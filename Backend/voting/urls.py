"""
COMITIA Voting URLs
Voting and blockchain integration endpoints
"""

from django.urls import path
from . import views

urlpatterns = [
    # Voting Session Management
    path('sessions/start/<uuid:election_id>/', views.start_voting_session, name='start-voting-session'),
    path('sessions/<uuid:session_id>/verify-biometric/', views.verify_biometric, name='verify-biometric'),
    path('sessions/<uuid:session_id>/status/', views.get_session_status, name='get-session-status'),
    
    # Vote Casting
    path('cast-vote/', views.cast_vote, name='cast-vote'),
    path('verify-vote/<str:verification_code>/', views.verify_vote, name='verify-vote'),
    
    # Vote History and Receipts
    path('my-votes/', views.get_my_votes, name='get-my-votes'),
    path('receipt/<uuid:vote_id>/', views.get_vote_receipt, name='get-vote-receipt'),
    
    # Blockchain Integration
    path('blockchain/status/<str:transaction_hash>/', views.get_blockchain_status, name='get-blockchain-status'),
    path('blockchain/verify/<str:vote_hash>/', views.verify_on_blockchain, name='verify-on-blockchain'),
    
    # Statistics (for officials)
    path('statistics/<uuid:election_id>/', views.get_voting_statistics, name='get-voting-statistics'),
]
