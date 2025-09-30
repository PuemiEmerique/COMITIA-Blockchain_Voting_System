"""
COMITIA User Serializers
Handle serialization for all 5 user types
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import (
    User, CitizenProfile, VoterProfile, CandidateProfile, 
    VoterOfficialProfile, ElectoralCommissionProfile, BiometricData
)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration (Citizens)
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number', 'national_id',
            'date_of_birth', 'address'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        
        # Create citizen profile by default
        CitizenProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include username and password')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information
    """
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    verification_status_display = serializers.CharField(source='get_verification_status_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_type', 'user_type_display', 'phone_number', 'national_id',
            'date_of_birth', 'address', 'verification_status', 
            'verification_status_display', 'is_biometric_registered',
            'registration_date', 'profile_picture', 'bio', 'ethereum_address'
        ]
        read_only_fields = ['id', 'user_type', 'verification_status', 'registration_date']


class CitizenProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Citizen profile
    """
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = CitizenProfile
        fields = [
            'user', 'occupation', 'education_level', 
            'voter_pre_enrollment_date', 'voter_pre_enrollment_status'
        ]


class VoterProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Voter profile
    """
    user = UserProfileSerializer(read_only=True)
    registration_completed_by_name = serializers.CharField(
        source='registration_completed_by.get_full_name', 
        read_only=True
    )
    
    class Meta:
        model = VoterProfile
        fields = [
            'user', 'voter_id', 'polling_station', 'constituency',
            'voter_card_issued', 'voter_card_number', 
            'registration_completed_by_name'
        ]


class CandidateProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Candidate profile
    """
    user = UserProfileSerializer(read_only=True)
    application_status_display = serializers.CharField(
        source='get_application_status_display', 
        read_only=True
    )
    approved_by_name = serializers.CharField(
        source='approved_by.get_full_name', 
        read_only=True
    )
    
    class Meta:
        model = CandidateProfile
        fields = [
            'user', 'candidate_id', 'political_party', 'campaign_slogan',
            'manifesto', 'application_status', 'application_status_display',
            'application_date', 'approved_by_name'
        ]


class CandidateApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for candidate application
    """
    class Meta:
        model = CandidateProfile
        fields = [
            'political_party', 'campaign_slogan', 'manifesto'
        ]


class VoterOfficialProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Voter Official profile
    """
    user = UserProfileSerializer(read_only=True)
    appointed_by_name = serializers.CharField(
        source='appointed_by.get_full_name', 
        read_only=True
    )
    
    class Meta:
        model = VoterOfficialProfile
        fields = [
            'user', 'official_id', 'assigned_region', 'registration_center',
            'appointment_date', 'appointed_by_name', 'is_active'
        ]


class ElectoralCommissionProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Electoral Commission profile
    """
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = ElectoralCommissionProfile
        fields = [
            'user', 'commission_id', 'position', 'jurisdiction',
            'appointment_date', 'term_end_date', 'is_active'
        ]


class BiometricDataSerializer(serializers.ModelSerializer):
    """
    Serializer for biometric data
    """
    registered_by_name = serializers.CharField(
        source='registered_by.get_full_name', 
        read_only=True
    )
    
    class Meta:
        model = BiometricData
        fields = [
            'face_image_path', 'registration_date', 
            'registered_by_name', 'is_verified'
        ]
        read_only_fields = ['registration_date', 'registered_by_name']


class VoterPreEnrollmentSerializer(serializers.Serializer):
    """
    Serializer for voter pre-enrollment application
    """
    occupation = serializers.CharField(max_length=100, required=False)
    education_level = serializers.CharField(max_length=50, required=False)
    
    def update(self, instance, validated_data):
        # Update citizen profile
        citizen_profile = instance.citizen_profile
        citizen_profile.occupation = validated_data.get('occupation', citizen_profile.occupation)
        citizen_profile.education_level = validated_data.get('education_level', citizen_profile.education_level)
        citizen_profile.voter_pre_enrollment_status = 'pending'
        citizen_profile.voter_pre_enrollment_date = timezone.now()
        citizen_profile.save()
        
        return instance


class UserRoleTransitionSerializer(serializers.Serializer):
    """
    Serializer for changing user roles (used by officials)
    """
    user_id = serializers.UUIDField()
    new_role = serializers.ChoiceField(choices=User.USER_TYPES)
    reason = serializers.CharField(max_length=500, required=False)
    
    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
