"""
COMITIA Admin Configuration
Admin interface for user management
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, CitizenProfile, VoterProfile, CandidateProfile,
    VoterOfficialProfile, ElectoralCommissionProfile, BiometricData, UserActivity
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin
    """
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'user_type', 'verification_status', 'is_biometric_registered',
        'registration_date', 'is_active'
    ]
    list_filter = [
        'user_type', 'verification_status', 'is_biometric_registered',
        'is_active', 'registration_date'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'national_id']
    ordering = ['-registration_date']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('COMITIA Profile', {
            'fields': (
                'user_type', 'phone_number', 'national_id', 'date_of_birth',
                'address', 'verification_status', 'is_biometric_registered',
                'profile_picture', 'bio', 'ethereum_address'
            )
        }),
    )


@admin.register(CitizenProfile)
class CitizenProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'occupation', 'education_level', 
        'voter_pre_enrollment_status', 'voter_pre_enrollment_date'
    ]
    list_filter = ['voter_pre_enrollment_status', 'education_level']
    search_fields = ['user__username', 'user__email', 'occupation']


@admin.register(VoterProfile)
class VoterProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'voter_id', 'polling_station', 'constituency',
        'voter_card_issued', 'registration_completed_by'
    ]
    list_filter = ['voter_card_issued', 'constituency']
    search_fields = ['user__username', 'voter_id', 'polling_station']


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'candidate_id', 'political_party', 'application_status',
        'application_date', 'approved_by'
    ]
    list_filter = ['application_status', 'political_party', 'application_date']
    search_fields = ['user__username', 'candidate_id', 'political_party']


@admin.register(VoterOfficialProfile)
class VoterOfficialProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'official_id', 'assigned_region', 'registration_center',
        'is_active', 'appointment_date', 'appointed_by'
    ]
    list_filter = ['is_active', 'assigned_region', 'appointment_date']
    search_fields = ['user__username', 'official_id', 'assigned_region']


@admin.register(ElectoralCommissionProfile)
class ElectoralCommissionProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'commission_id', 'position', 'jurisdiction',
        'is_active', 'appointment_date', 'term_end_date'
    ]
    list_filter = ['is_active', 'position', 'jurisdiction']
    search_fields = ['user__username', 'commission_id', 'position']


@admin.register(BiometricData)
class BiometricDataAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'is_verified', 'registration_date', 'registered_by'
    ]
    list_filter = ['is_verified', 'registration_date']
    search_fields = ['user__username', 'user__email']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'activity_type', 'description', 'timestamp', 'ip_address'
    ]
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['user__username', 'description', 'ip_address']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
