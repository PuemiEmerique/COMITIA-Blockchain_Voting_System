#!/usr/bin/env python
"""
Simple Test Runner for COMITIA
Runs comprehensive tests and generates a detailed report
"""

import os
import sys
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comitia.settings')
django.setup()

from django.test import TestCase
from django.test.utils import get_runner
from django.conf import settings
from django.core.management import execute_from_command_line


def run_comprehensive_tests():
    """Run comprehensive tests with detailed reporting"""
    
    print("🧪 COMITIA COMPREHENSIVE TEST REPORT")
    print("=" * 80)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️  Environment: {settings.DEBUG and 'Development' or 'Production'}")
    print(f"🗄️  Database: {settings.DATABASES['default']['ENGINE'].split('.')[-1]}")
    print("=" * 80)
    
    # Test categories to run
    test_categories = [
        {
            'name': '1. USER MODEL TESTING',
            'description': 'Testing user creation, properties, and validation',
            'command': ['test', 'accounts.tests.UserModelTest', '--verbosity=0']
        },
        {
            'name': '2. AUTHENTICATION TESTING', 
            'description': 'Testing login, logout, and registration',
            'command': ['test', 'accounts.tests.AuthenticationViewTests', '--verbosity=0']
        },
        {
            'name': '3. DASHBOARD TESTING',
            'description': 'Testing role-based dashboard access',
            'command': ['test', 'accounts.tests.DashboardViewTests', '--verbosity=0']
        },
        {
            'name': '4. PERMISSION TESTING',
            'description': 'Testing user permissions and access control',
            'command': ['test', 'accounts.tests.PermissionTests', '--verbosity=0']
        },
        {
            'name': '5. MODEL VALIDATION TESTING',
            'description': 'Testing model constraints and validation',
            'command': ['test', 'accounts.tests.ModelValidationTests', '--verbosity=0']
        }
    ]
    
    results = []
    
    for category in test_categories:
        print(f"\n🔍 {category['name']}")
        print(f"📝 {category['description']}")
        print("-" * 60)
        
        try:
            # Capture the test output
            import subprocess
            import sys
            
            cmd = [sys.executable, 'manage.py'] + category['command']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                print("✅ PASSED")
                # Extract test count from output
                lines = result.stderr.split('\n')
                for line in lines:
                    if 'Ran' in line and 'test' in line:
                        print(f"📊 {line.strip()}")
                        break
                results.append({'category': category['name'], 'status': 'PASSED', 'details': result.stderr})
            else:
                print("❌ FAILED")
                print("🔍 Error Details:")
                error_lines = result.stderr.split('\n')
                for line in error_lines[-10:]:  # Show last 10 lines
                    if line.strip():
                        print(f"   {line}")
                results.append({'category': category['name'], 'status': 'FAILED', 'details': result.stderr})
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({'category': category['name'], 'status': 'ERROR', 'details': str(e)})
    
    # Generate summary report
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in results if r['status'] == 'PASSED')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"🚨 Errors: {errors}")
    print(f"📈 Success Rate: {(passed / len(results) * 100):.1f}%")
    
    print("\n📋 DETAILED RESULTS:")
    print("-" * 40)
    for result in results:
        status_icon = "✅" if result['status'] == 'PASSED' else "❌"
        print(f"{status_icon} {result['category']}: {result['status']}")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED! Your COMITIA application is working correctly.")
    else:
        print(f"\n⚠️  {failed + errors} test categories need attention.")
    
    print("=" * 80)
    return results


def run_specific_functionality_tests():
    """Run tests for specific functionalities"""
    
    print("\n🎯 SPECIFIC FUNCTIONALITY TESTS")
    print("=" * 50)
    
    # Define specific functionality tests
    functionalities = [
        {
            'name': 'User Registration',
            'test': 'test_register_view_post_valid',
            'description': 'Tests if users can register successfully'
        },
        {
            'name': 'User Login',
            'test': 'test_login_view_post_valid', 
            'description': 'Tests if users can login with valid credentials'
        },
        {
            'name': 'Dashboard Access',
            'test': 'test_citizen_dashboard_access',
            'description': 'Tests if users can access their dashboards'
        },
        {
            'name': 'User Permissions',
            'test': 'test_voting_permissions',
            'description': 'Tests if user permissions work correctly'
        }
    ]
    
    for func in functionalities:
        print(f"\n🔍 Testing: {func['name']}")
        print(f"📝 {func['description']}")
        print("-" * 30)
        
        try:
            # Run specific test
            cmd = ['test', f'accounts.tests.AuthenticationViewTests.{func["test"]}', '--verbosity=1']
            result = subprocess.run([sys.executable, 'manage.py'] + cmd, 
                                  capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                print("✅ WORKING CORRECTLY")
            else:
                print("❌ NEEDS ATTENTION")
                print("🔍 Issue found - check implementation")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")


def main():
    """Main function to run tests"""
    print("🚀 COMITIA TESTING SUITE")
    print("=" * 30)
    print("1. Run Comprehensive Tests")
    print("2. Run Specific Functionality Tests")
    print("3. Run Both")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == '1':
        run_comprehensive_tests()
    elif choice == '2':
        run_specific_functionality_tests()
    elif choice == '3':
        run_comprehensive_tests()
        run_specific_functionality_tests()
    elif choice == '4':
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice!")
        return


if __name__ == '__main__':
    main()
