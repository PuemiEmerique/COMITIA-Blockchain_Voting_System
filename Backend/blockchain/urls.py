"""
COMITIA Blockchain URLs
Blockchain integration endpoints
"""

from django.urls import path
from . import views

urlpatterns = [
    # Smart Contract Management
    path('deploy-contract/', views.deploy_voting_contract, name='deploy-voting-contract'),
    path('contract-info/', views.get_contract_info, name='get-contract-info'),
    
    # Blockchain Operations
    path('register-voter/<uuid:user_id>/', views.register_voter_on_blockchain, name='register-voter-blockchain'),
    path('create-election/<uuid:election_id>/', views.create_election_on_blockchain, name='create-election-blockchain'),
    
    # Transaction Monitoring
    path('transactions/', views.get_blockchain_transactions, name='get-blockchain-transactions'),
    path('transaction/<str:tx_hash>/', views.get_transaction_status, name='get-transaction-status'),
    
    # Network Status
    path('network-status/', views.get_network_status, name='get-network-status'),
]
