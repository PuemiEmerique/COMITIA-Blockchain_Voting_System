"""
Management command to create test users for all 5 user types
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User, CitizenProfile, VoterProfile, CandidateProfile
from accounts.models import VoterOfficialProfile, ElectoralCommissionProfile


class Command(BaseCommand):
    help = 'Create test users for all 5 user types'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating test users for COMITIA system...'))
        
        with transaction.atomic():
            # Create Citizen user
            citizen_user, created = User.objects.get_or_create(
                username='citizen_test',
                defaults={
                    'email': 'citizen@comitia.com',
                    'first_name': 'John',
                    'last_name': 'Citizen',
                    'user_type': 'citizen',
                    'verification_status': 'pending',
                }
            )
            if created:
                citizen_user.set_password('testpass123')
                citizen_user.save()
                CitizenProfile.objects.get_or_create(user=citizen_user)
                self.stdout.write(f'[+] Created Citizen user: {citizen_user.username}')
            else:
                self.stdout.write(f'[-] Citizen user already exists: {citizen_user.username}')

            # Create Voter user
            voter_user, created = User.objects.get_or_create(
                username='voter_test',
                defaults={
                    'email': 'voter@comitia.com',
                    'first_name': 'Jane',
                    'last_name': 'Voter',
                    'user_type': 'voter',
                    'verification_status': 'approved',
                }
            )
            if created:
                voter_user.set_password('testpass123')
                voter_user.save()
                VoterProfile.objects.get_or_create(user=voter_user)
                self.stdout.write(f'[+] Created Voter user: {voter_user.username}')
            else:
                self.stdout.write(f'[-] Voter user already exists: {voter_user.username}')

            # Create Candidate user
            candidate_user, created = User.objects.get_or_create(
                username='candidate_test',
                defaults={
                    'email': 'candidate@comitia.com',
                    'first_name': 'Bob',
                    'last_name': 'Candidate',
                    'user_type': 'candidate',
                    'verification_status': 'approved',
                    'bio': 'Experienced leader committed to positive change in our community.',
                }
            )
            if created:
                candidate_user.set_password('testpass123')
                candidate_user.save()
                CandidateProfile.objects.get_or_create(user=candidate_user)
                self.stdout.write(f'✓ Created Candidate user: {candidate_user.username}')
            else:
                self.stdout.write(f'- Candidate user already exists: {candidate_user.username}')

            # Create Voter Official user
            official_user, created = User.objects.get_or_create(
                username='official_test',
                defaults={
                    'email': 'official@comitia.com',
                    'first_name': 'Alice',
                    'last_name': 'Official',
                    'user_type': 'voter_official',
                    'verification_status': 'approved',
                }
            )
            if created:
                official_user.set_password('testpass123')
                official_user.save()
                VoterOfficialProfile.objects.get_or_create(user=official_user)
                self.stdout.write(f'✓ Created Voter Official user: {official_user.username}')
            else:
                self.stdout.write(f'- Voter Official user already exists: {official_user.username}')

            # Create Electoral Commission user
            commission_user, created = User.objects.get_or_create(
                username='commission_test',
                defaults={
                    'email': 'commission@comitia.com',
                    'first_name': 'David',
                    'last_name': 'Commissioner',
                    'user_type': 'electoral_commission',
                    'verification_status': 'approved',
                }
            )
            if created:
                commission_user.set_password('testpass123')
                commission_user.save()
                ElectoralCommissionProfile.objects.get_or_create(user=commission_user)
                self.stdout.write(f'✓ Created Electoral Commission user: {commission_user.username}')
            else:
                self.stdout.write(f'- Electoral Commission user already exists: {commission_user.username}')

        self.stdout.write(self.style.SUCCESS('\n=== Test Users Created Successfully ==='))
        self.stdout.write('Login credentials for all test users:')
        self.stdout.write('Password: testpass123')
        self.stdout.write('')
        self.stdout.write('Test user accounts:')
        self.stdout.write('• Citizen: citizen_test / testpass123')
        self.stdout.write('• Voter: voter_test / testpass123')
        self.stdout.write('• Candidate: candidate_test / testpass123')
        self.stdout.write('• Voter Official: official_test / testpass123')
        self.stdout.write('• Electoral Commission: commission_test / testpass123')
        self.stdout.write('')
        self.stdout.write('You can now test the different dashboards by logging in with these accounts.')
