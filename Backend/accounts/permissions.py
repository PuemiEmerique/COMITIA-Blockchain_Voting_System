"""
COMITIA Custom Permissions
Role-based permissions for the 5-actor system
"""

from rest_framework import permissions


class IsElectoralCommission(permissions.BasePermission):
    """
    Permission for Electoral Commission members only
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_electoral_commission
        )


class IsVoterOfficial(permissions.BasePermission):
    """
    Permission for Voter Officials only
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_voter_official
        )


class IsVoterOfficialOrElectoralCommission(permissions.BasePermission):
    """
    Permission for Voter Officials or Electoral Commission members
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_voter_official or request.user.is_electoral_commission)
        )


class IsCandidate(permissions.BasePermission):
    """
    Permission for Candidates only
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_candidate
        )


class IsVoter(permissions.BasePermission):
    """
    Permission for Voters only
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_voter
        )


class CanVote(permissions.BasePermission):
    """
    Permission for users who can vote (Voters and approved Candidates)
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.can_vote
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj == request.user or obj.user == request.user


class IsApprovedUser(permissions.BasePermission):
    """
    Permission for approved users only
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.verification_status == 'approved'
        )


class IsBiometricRegistered(permissions.BasePermission):
    """
    Permission for users with biometric registration
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_biometric_registered
        )
