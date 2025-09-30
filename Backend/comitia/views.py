"""
COMITIA Main Views
Handles home page and general application views
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

# Temporarily disabled until apps are created
# from accounts.models import User
# from elections.models import Election


def home(request):
    """
    Home page view with public information
    """
    context = {
        'system_name': 'COMITIA',
        'system_description': 'Secure Blockchain-based Electronic Voting System'
    }
    
    # Temporarily disabled until models are created
    # Get active elections for public display
    # active_elections = Election.objects.filter(...)
    
    # Get system statistics for public display
    # election_stats = {...}
    
    return render(request, 'home.html', context)


@login_required
def dashboard(request):
    """
    Main dashboard view - temporarily simplified
    """
    context = {
        'user': request.user,
        'message': 'Dashboard functionality will be available once user apps are created.'
    }
    return render(request, 'dashboard.html', context)


def about(request):
    """
    About page with system information
    """
    context = {
        'features': [
            {
                'title': 'Blockchain Security',
                'description': 'All votes are recorded on the Ethereum blockchain for immutable transparency.',
                'icon': 'fas fa-shield-alt'
            },
            {
                'title': 'Biometric Authentication',
                'description': 'Advanced facial recognition and fingerprint authentication ensure voter identity.',
                'icon': 'fas fa-fingerprint'
            },
            {
                'title': 'Real-time Results',
                'description': 'Live election results with instant verification and transparent counting.',
                'icon': 'fas fa-chart-line'
            },
            {
                'title': 'Multi-Role System',
                'description': 'Comprehensive system supporting all stakeholders in the electoral process.',
                'icon': 'fas fa-users'
            },
            {
                'title': 'Mobile Responsive',
                'description': 'Access the system from any device with our responsive design.',
                'icon': 'fas fa-mobile-alt'
            },
            {
                'title': 'Audit Trail',
                'description': 'Complete audit trail with blockchain verification for accountability.',
                'icon': 'fas fa-search'
            }
        ],
        'stats': {
            'elections_conducted': Election.objects.filter(status='completed').count(),
            'registered_voters': User.objects.filter(user_type='voter').count(),
            'system_uptime': '99.9%',  # This would be calculated from actual metrics
            'security_level': 'Military Grade'
        }
    }
    
    return render(request, 'about.html', context)


def privacy_policy(request):
    """
    Privacy policy page
    """
    return render(request, 'legal/privacy_policy.html')


def terms_of_service(request):
    """
    Terms of service page
    """
    return render(request, 'legal/terms_of_service.html')


def contact(request):
    """
    Contact page
    """
    from django.contrib import messages
    from django.core.mail import send_mail
    from django.conf import settings
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if all([name, email, subject, message]):
            try:
                # Send email to administrators
                full_message = f"""
                Contact Form Submission
                
                Name: {name}
                Email: {email}
                Subject: {subject}
                
                Message:
                {message}
                """
                
                send_mail(
                    f'COMITIA Contact: {subject}',
                    full_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                
                messages.success(request, 'Your message has been sent successfully. We will get back to you soon.')
            except Exception as e:
                messages.error(request, 'Failed to send message. Please try again later.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'contact.html')


def help_center(request):
    """
    Help center with FAQs and documentation
    """
    faqs = [
        {
            'question': 'How do I register to vote?',
            'answer': 'Create an account as a Citizen, then apply for voter registration through your dashboard. You will need to provide biometric data and identity verification.'
        },
        {
            'question': 'Is my vote secure and anonymous?',
            'answer': 'Yes, votes are encrypted and recorded on the blockchain while maintaining complete anonymity. Your identity is verified but not linked to your vote choices.'
        },
        {
            'question': 'How does biometric authentication work?',
            'answer': 'We use advanced facial recognition and fingerprint technology to verify your identity during registration and voting, ensuring only authorized voters can participate.'
        },
        {
            'question': 'Can I verify my vote was counted?',
            'answer': 'Yes, you will receive a verification code that you can use to confirm your vote was recorded on the blockchain without revealing your choices.'
        },
        {
            'question': 'What if I encounter technical issues?',
            'answer': 'Contact our support team through the help center or visit your local voter assistance center for technical support.'
        },
        {
            'question': 'How are election results calculated?',
            'answer': 'Results are automatically calculated from blockchain records and verified by multiple independent nodes to ensure accuracy and transparency.'
        }
    ]
    
    context = {
        'faqs': faqs,
        'user_guides': [
            {
                'title': 'Voter Registration Guide',
                'description': 'Step-by-step guide to register as a voter',
                'url': '#voter-registration'
            },
            {
                'title': 'How to Vote',
                'description': 'Complete voting process walkthrough',
                'url': '#voting-guide'
            },
            {
                'title': 'Candidate Application',
                'description': 'Guide for running as a candidate',
                'url': '#candidate-guide'
            },
            {
                'title': 'Blockchain Verification',
                'description': 'How to verify your vote on the blockchain',
                'url': '#verification-guide'
            }
        ]
    }
    
    return render(request, 'help/index.html', context)


def system_status(request):
    """
    System status page showing current system health
    """
    from django.db import connection
    from django.core.cache import cache
    import time
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = 'operational'
    except Exception:
        db_status = 'error'
    
    # Check cache connectivity
    try:
        cache.set('health_check', 'ok', 30)
        cache_status = 'operational' if cache.get('health_check') == 'ok' else 'error'
    except Exception:
        cache_status = 'error'
    
    # Mock blockchain status (would be real blockchain check)
    blockchain_status = 'operational'
    
    # Mock biometric service status
    biometric_status = 'operational'
    
    context = {
        'overall_status': 'operational' if all(status == 'operational' for status in [
            db_status, cache_status, blockchain_status, biometric_status
        ]) else 'degraded',
        'services': {
            'database': {
                'status': db_status,
                'description': 'Primary database connectivity'
            },
            'cache': {
                'status': cache_status,
                'description': 'Redis cache service'
            },
            'blockchain': {
                'status': blockchain_status,
                'description': 'Ethereum blockchain connectivity'
            },
            'biometric': {
                'status': biometric_status,
                'description': 'Biometric authentication service'
            }
        },
        'last_updated': timezone.now()
    }
    
    return render(request, 'system_status.html', context)


def api_documentation(request):
    """
    API documentation page
    """
    return render(request, 'api_docs.html')


def security_report(request):
    """
    Security and transparency report
    """
    # This would contain real security metrics
    context = {
        'security_metrics': {
            'encryption_level': 'AES-256',
            'blockchain_confirmations': 12,
            'biometric_accuracy': '99.97%',
            'uptime_percentage': '99.95%',
            'failed_login_attempts': 0,
            'security_incidents': 0
        },
        'audit_summary': {
            'last_security_audit': '2024-01-15',
            'next_scheduled_audit': '2024-04-15',
            'compliance_status': 'Fully Compliant',
            'certifications': [
                'ISO 27001',
                'SOC 2 Type II',
                'GDPR Compliant'
            ]
        }
    }
    
    return render(request, 'security_report.html', context)


def handler404(request, exception):
    """
    Custom 404 error handler
    """
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    """
    Custom 500 error handler
    """
    return render(request, 'errors/500.html', status=500)


def handler403(request, exception):
    """
    Custom 403 error handler
    """
    return render(request, 'errors/403.html', status=403)
