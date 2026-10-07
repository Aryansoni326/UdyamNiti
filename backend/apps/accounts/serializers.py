"""
Serializers for Authentication, Identity, and Security Profiles.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserSecurityProfile, UserRole, SecurityAuditLog


class UserSecurityProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSecurityProfile
        fields = ['role', 'mfa_enabled', 'failed_login_attempts', 'locked_until', 'created_at']


class UserDetailSerializer(serializers.ModelSerializer):
    security_profile = UserSecurityProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'security_profile']


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class RegisterRequestSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    role = serializers.ChoiceField(choices=UserRole.choices, default=UserRole.MSME_USER)


class SecurityAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityAuditLog
        fields = ['id', 'timestamp', 'actor_username', 'action', 'resource_type', 'resource_id', 'status', 'details']
