"""
Security and Identity Domain Models.
Implements:
1. UserSecurityProfile: Role-Based Access Control (RBAC), account lockouts, MFA tracking.
2. SecurityAuditLog: Immutable audit log for security events, object access violations, and admin actions.
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserRole(models.TextChoices):
    MSME_USER = 'msme_user', 'MSME Business Owner / Representative'
    POLICY_ANALYST = 'policy_analyst', 'Government Policy Analyst'
    COMPLIANCE_OFFICER = 'compliance_officer', 'Compliance Officer'
    SYSTEM_ADMIN = 'system_admin', 'System Administrator'


class UserSecurityProfile(models.Model):
    """
    Extends Django's User model with RBAC roles, security controls, and session metadata.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='security_profile')
    role = models.CharField(max_length=30, choices=UserRole.choices, default=UserRole.MSME_USER)

    # Brute-force protection
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    # Password hygiene & MFA
    password_changed_at = models.DateTimeField(auto_now_add=True)
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=64, blank=True, help_text="TOTP Secret Key (AES encrypted in prod)")

    # Compliance & Consent
    privacy_consent_at = models.DateTimeField(null=True, blank=True)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'auth_user_security_profiles'
        verbose_name = 'User Security Profile'
        verbose_name_plural = 'User Security Profiles'

    def is_locked(self) -> bool:
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False

    def reset_failed_logins(self):
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def register_failed_login(self, max_attempts: int = 5, lock_minutes: int = 15):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_attempts:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=lock_minutes)
        self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def __str__(self):
        return f"{self.user.username} [{self.role}]"


class AuditAction(models.TextChoices):
    LOGIN_SUCCESS = 'login_success', 'User Login Successful'
    LOGIN_FAILED = 'login_failed', 'Failed Login Attempt'
    ACCOUNT_LOCKED = 'account_locked', 'Account Locked due to Brute-Force'
    PERMISSION_DENIED = 'permission_denied', 'Unauthorized Object Access Denied'
    PROFILE_CREATED = 'profile_created', 'Business Profile Created'
    PROFILE_UPDATED = 'profile_updated', 'Business Profile Updated'
    DOCUMENT_UPLOADED = 'document_uploaded', 'Document Uploaded'
    DOCUMENT_DELETED = 'document_deleted', 'Document Deleted'
    STRATEGY_GENERATED = 'strategy_generated', 'Strategy Plan Generated'
    POLICY_CHANGE_APPROVED = 'policy_change_approved', 'Policy Change Approved by Admin'
    SECURITY_SETTING_CHANGED = 'security_setting_changed', 'Security Configuration Changed'


class SecurityAuditLog(models.Model):
    """
    Immutable security audit trail recording user identity, IP address, resource accessed,
    action performed, and authorization decision.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    actor_username = models.CharField(max_length=150, blank=True, help_text="Preserved username in case user is deleted")

    action = models.CharField(max_length=40, choices=AuditAction.choices, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    resource_type = models.CharField(max_length=100, blank=True, help_text="e.g. BusinessProfile, BusinessDocument")
    resource_id = models.CharField(max_length=100, blank=True, help_text="Target entity UUID")

    status = models.CharField(max_length=20, default='SUCCESS', choices=[('SUCCESS', 'Success'), ('DENIED', 'Denied'), ('FAILURE', 'Failure')])
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'auth_security_audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.action} by {self.actor_username or 'Anonymous'} ({self.status})"
