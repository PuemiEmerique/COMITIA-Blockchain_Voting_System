"""
COMITIA Elections Admin Configuration
"""

from django.contrib import admin
from .models import (
    Election, ElectionPosition, ElectionCandidate, ElectionConstituency,
    PollingStation, ElectionResult, ElectionAuditLog, ElectionNotification
)


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'election_type', 'status', 'voting_start_date',
        'voting_end_date', 'total_votes_cast', 'results_published'
    ]
    list_filter = ['election_type', 'status', 'results_published', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'total_votes_cast', 'total_eligible_voters']
    ordering = ['-created_at']


@admin.register(ElectionPosition)
class ElectionPositionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'election', 'max_votes_per_voter', 'available_seats',
        'minimum_age', 'display_order', 'is_active'
    ]
    list_filter = ['election', 'is_active', 'minimum_age']
    search_fields = ['title', 'election__title']
    ordering = ['election', 'display_order']


@admin.register(ElectionCandidate)
class ElectionCandidateAdmin(admin.ModelAdmin):
    list_display = [
        'candidate', 'election', 'position', 'status', 'ballot_number',
        'total_votes', 'registration_date'
    ]
    list_filter = ['status', 'election', 'position', 'registration_date']
    search_fields = ['candidate__username', 'candidate__first_name', 'candidate__last_name']
    readonly_fields = ['registration_date', 'total_votes', 'vote_percentage']
    ordering = ['election', 'position', 'ballot_number']


@admin.register(ElectionConstituency)
class ElectionConstituencyAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'code', 'election', 'region', 'state_province',
        'registered_voters_count'
    ]
    list_filter = ['election', 'region', 'state_province']
    search_fields = ['name', 'code']
    ordering = ['election', 'name']


@admin.register(PollingStation)
class PollingStationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'code', 'constituency', 'capacity',
        'assigned_voters_count', 'presiding_officer', 'is_active'
    ]
    list_filter = ['constituency__election', 'is_active']
    search_fields = ['name', 'code', 'address']
    ordering = ['constituency', 'name']


@admin.register(ElectionResult)
class ElectionResultAdmin(admin.ModelAdmin):
    list_display = [
        'candidate', 'election', 'position', 'total_votes',
        'vote_percentage', 'rank', 'is_winner', 'is_verified'
    ]
    list_filter = ['election', 'position', 'is_winner', 'is_verified']
    search_fields = ['candidate__candidate__username']
    readonly_fields = ['calculated_at', 'published_at']
    ordering = ['election', 'position', 'rank']


@admin.register(ElectionAuditLog)
class ElectionAuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'election', 'action', 'performed_by', 'timestamp', 'ip_address'
    ]
    list_filter = ['action', 'election', 'timestamp']
    search_fields = ['election__title', 'performed_by__username', 'description']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']


@admin.register(ElectionNotification)
class ElectionNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'election', 'notification_type', 'is_sent',
        'sent_at', 'scheduled_for'
    ]
    list_filter = ['notification_type', 'is_sent', 'election']
    search_fields = ['title', 'message', 'election__title']
    readonly_fields = ['created_at', 'sent_at']
    ordering = ['-created_at']
