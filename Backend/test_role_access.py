#!/usr/bin/env python
"""
Test script to verify role-based dashboard access
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comitia.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def test_role_access():
    print("🧪 Testing Role-Based Dashboard Access")
    print("=" * 50)
    
    # Create test client
    client = Client()
    
    # Create or get superuser
    try:
        admin_user = User.objects.get(username='admin')
        print("✅ Using existing admin user")
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@comitia.com',
            password='admin123'
        )
        print("✅ Created new admin user")
    
    # Test role-based login
    print("\n🔐 Testing Role-Based Login...")
    
    # Login with role selection
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'selected_role': 'voter_official'
    }
    
    response = client.post(reverse('accounts:role_login'), login_data)
    print(f"✅ Role login response: {response.status_code}")
    
    # Test voter official dashboard access
    print("\n👮 Testing Voter Official Dashboard Access...")
    response = client.get(reverse('accounts:voter_official_dashboard'))
    if response.status_code == 200:
        print("✅ Voter Official dashboard accessible!")
    else:
        print(f"❌ Voter Official dashboard failed: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"Response: {response.content[:200]}")
    
    # Test electoral commission dashboard
    print("\n🏛️ Testing Electoral Commission Dashboard Access...")
    
    # Set session for electoral commission
    session = client.session
    session['selected_role'] = 'electoral_commission'
    session.save()
    
    response = client.get(reverse('accounts:electoral_commission_dashboard'))
    if response.status_code == 200:
        print("✅ Electoral Commission dashboard accessible!")
    else:
        print(f"❌ Electoral Commission dashboard failed: {response.status_code}")
    
    # Test superadmin dashboard
    print("\n👑 Testing Super Admin Dashboard Access...")
    response = client.get(reverse('accounts:superadmin_dashboard'))
    if response.status_code == 200:
        print("✅ Super Admin dashboard accessible!")
    else:
        print(f"❌ Super Admin dashboard failed: {response.status_code}")
    
    print("\n🎯 Role access test completed!")
    print("All dashboards should now be accessible via role-based login.")

if __name__ == '__main__':
    test_role_access()
