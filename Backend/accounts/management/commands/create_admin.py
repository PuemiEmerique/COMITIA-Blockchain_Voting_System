"""
Django management command to create a superuser for COMITIA system
Usage: python manage.py create_admin
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
import getpass

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser for COMITIA system with role-based login access'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the superuser',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email for the superuser',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the superuser',
        )
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Create superuser without prompting for input',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 COMITIA Superuser Creation Tool\n')
        )

        # Get username
        username = options.get('username')
        if not username:
            username = input('Username (admin): ') or 'admin'

        # Get email
        email = options.get('email')
        if not email:
            email = input('Email (admin@comitia.com): ') or 'admin@comitia.com'

        # Get password
        password = options.get('password')
        if not password and not options.get('no_input'):
            while True:
                password = getpass.getpass('Password: ')
                password_confirm = getpass.getpass('Confirm password: ')
                if password == password_confirm:
                    break
                else:
                    self.stdout.write(
                        self.style.ERROR('Passwords do not match. Please try again.')
                    )
        elif not password:
            password = 'admin123'  # Default password for --no-input

        try:
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" already exists!')
                )
                
                # Ask if user wants to update existing user
                if not options.get('no_input'):
                    update = input('Update existing user to superuser? (y/N): ')
                    if update.lower() in ['y', 'yes']:
                        user = User.objects.get(username=username)
                        user.is_superuser = True
                        user.is_staff = True
                        user.set_password(password)
                        user.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Updated "{username}" to superuser!')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING('Operation cancelled.')
                        )
                        return
                else:
                    return

            else:
                # Create new superuser
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                
                # Set additional fields
                user.first_name = 'System'
                user.last_name = 'Administrator'
                user.user_type = 'citizen'  # Default user type
                user.save()

                self.stdout.write(
                    self.style.SUCCESS(f'✅ Superuser "{username}" created successfully!')
                )

            # Display login information
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.SUCCESS('🎯 LOGIN INFORMATION'))
            self.stdout.write('='*50)
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Email: {email}')
            self.stdout.write(f'Password: {"*" * len(password)}')
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.SUCCESS('🚀 ACCESS METHODS'))
            self.stdout.write('='*50)
            self.stdout.write('1. Regular Login: /accounts/login/')
            self.stdout.write('2. Role-Based Login: /accounts/role-login/')
            self.stdout.write('3. Django Admin: /admin/')
            self.stdout.write('4. Super Admin Dashboard: /accounts/dashboard/superadmin/')
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.SUCCESS('✨ FEATURES AVAILABLE'))
            self.stdout.write('='*50)
            self.stdout.write('• Access all role dashboards')
            self.stdout.write('• Switch between user roles')
            self.stdout.write('• Manage users and system')
            self.stdout.write('• Test all user experiences')
            self.stdout.write('• Full database access')
            self.stdout.write('\n')

        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )
