#!/usr/bin/env python
"""
Quick setup script for COMITIA Admin
Creates superuser and provides access information
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_admin():
    """Setup Django environment and create admin user"""
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comitia.settings')
    django.setup()
    
    print("🚀 COMITIA Admin Setup")
    print("=" * 50)
    
    # Run migrations first
    print("📦 Running migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed!")
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return
    
    print("\n👤 Creating superuser...")
    
    # Create superuser
    try:
        execute_from_command_line(['manage.py', 'create_admin', '--no-input'])
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        return
    
    print("\n🌐 Starting development server...")
    print("Access your admin at:")
    print("• Regular Login: http://127.0.0.1:8000/accounts/login/")
    print("• Role Login: http://127.0.0.1:8000/accounts/role-login/")
    print("• Django Admin: http://127.0.0.1:8000/admin/")
    print("\nDefault credentials:")
    print("Username: admin")
    print("Password: admin123")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start server
    try:
        execute_from_command_line(['manage.py', 'runserver'])
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")

if __name__ == '__main__':
    setup_admin()
