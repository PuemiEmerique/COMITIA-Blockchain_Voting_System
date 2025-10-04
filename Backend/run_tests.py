#!/usr/bin/env python
"""
COMITIA Unit Test Runner
Simple script to run all unit tests with detailed output
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.test.utils import get_runner
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comitia.settings')
django.setup()

def run_all_tests():
    """Run all unit tests with verbose output"""
    print("🧪 COMITIA Unit Test Suite")
    print("=" * 50)
    
    # Test commands to run
    test_commands = [
        # Run all tests with verbose output
        ['test', '--verbosity=2', '--keepdb'],
        
        # Run specific app tests
        # ['test', 'accounts', '--verbosity=2'],
        # ['test', 'elections', '--verbosity=2'],
    ]
    
    for command in test_commands:
        print(f"\n🚀 Running: python manage.py {' '.join(command)}")
        print("-" * 40)
        
        try:
            execute_from_command_line(['manage.py'] + command)
        except SystemExit as e:
            if e.code != 0:
                print(f"❌ Tests failed with exit code: {e.code}")
                return False
            else:
                print("✅ Tests completed successfully!")
    
    return True

def run_specific_tests():
    """Run specific test categories"""
    print("\n📋 Available Test Categories:")
    print("-" * 30)
    
    test_categories = {
        '1': ('accounts.tests.UserModelTest', 'User Model Tests'),
        '2': ('accounts.tests.AuthenticationViewTests', 'Authentication Tests'),
        '3': ('accounts.tests.DashboardViewTests', 'Dashboard Tests'),
        '4': ('elections.tests.ElectionModelTest', 'Election Model Tests'),
        '5': ('elections.tests.ElectionBusinessLogicTest', 'Election Business Logic Tests'),
        '6': ('all', 'All Tests')
    }
    
    for key, (test_path, description) in test_categories.items():
        print(f"{key}. {description}")
    
    choice = input("\nSelect test category (1-6): ").strip()
    
    if choice in test_categories:
        test_path, description = test_categories[choice]
        print(f"\n🧪 Running: {description}")
        print("-" * 40)
        
        if test_path == 'all':
            return run_all_tests()
        else:
            try:
                execute_from_command_line(['manage.py', 'test', test_path, '--verbosity=2'])
                return True
            except SystemExit as e:
                return e.code == 0
    else:
        print("❌ Invalid choice!")
        return False

def main():
    """Main function"""
    print("🧪 COMITIA Unit Testing")
    print("=" * 30)
    print("1. Run All Tests")
    print("2. Run Specific Tests")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        success = run_all_tests()
    elif choice == '2':
        success = run_specific_tests()
    elif choice == '3':
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice!")
        return
    
    if success:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n❌ Some tests failed. Check the output above.")

if __name__ == '__main__':
    main()
