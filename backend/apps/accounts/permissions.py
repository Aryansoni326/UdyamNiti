"""
Object-Level & Role-Based Access Control (RBAC) Permissions.
Guarantees strict tenant/user isolation:
Users can only read, update, or delete their own profiles, documents, strategies, and application workspaces.
Staff/admins have read-only or elevated audit access based on role.
"""
from rest_framework import permissions
from .models import UserRole, SecurityAuditLog, AuditAction


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission allowing access ONLY to the owner of the object,
    or to staff/system administrators.
    Checks:
    - obj.user == request.user
    - obj.business_profile.user == request.user (for documents, strategies, workspaces)
    """
    def has_permission(self, request, view):
        # Must be authenticated to access user-owned resources
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Admins & Staff have access
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Check direct ownership (e.g. BusinessProfile.user)
        if hasattr(obj, 'user') and (obj.user == request.user or obj.user is None):
            return True

        # Check nested profile ownership (e.g. BusinessDocument.business_profile.user)
        if hasattr(obj, 'business_profile') and obj.business_profile:
            if obj.business_profile.user == request.user or obj.business_profile.user is None:
                return True

        # Check strategy ownership (e.g. ActionTask.strategy.business_profile.user)
        if hasattr(obj, 'strategy') and obj.strategy and obj.strategy.business_profile:
            if obj.strategy.business_profile.user == request.user or obj.strategy.business_profile.user is None:
                return True

        # Unauthorized access attempt - log security event
        SecurityAuditLog.objects.create(
            user=request.user,
            actor_username=request.user.username,
            action=AuditAction.PERMISSION_DENIED,
            resource_type=obj.__class__.__name__,
            resource_id=str(getattr(obj, 'id', 'unknown')),
            status='DENIED',
            details={
                'view': view.__class__.__name__,
                'method': request.method,
                'path': request.path
            }
        )
        return False


class IsPolicyAdmin(permissions.BasePermission):
    """
    Allows access to government policy analysts and system admins for managing schemes,
    approving detected policy changes, and inspecting ingestion reports.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.user.is_staff or request.user.is_superuser:
            return True

        # Check security profile role
        sec_profile = getattr(request.user, 'security_profile', None)
        if sec_profile and sec_profile.role in [UserRole.POLICY_ANALYST, UserRole.SYSTEM_ADMIN]:
            return True

        return False


class ReadOnlyOrAdmin(permissions.BasePermission):
    """
    Public/unauthenticated read access for catalog items (e.g. public schemes),
    but mutations require admin privileges.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and (request.user.is_staff or request.user.is_superuser))


def filter_user_queryset(queryset, user, profile_path: str = 'user'):
    """
    Helper utility to automatically scope querysets to the requesting user.
    If user is staff/admin, returns full queryset. Otherwise filters by owner.
    """
    if not user or not user.is_authenticated:
        return queryset.none()

    if user.is_staff or user.is_superuser:
        return queryset

    # Build filter e.g. user=user or business_profile__user=user
    filter_kwargs = {profile_path: user}
    return queryset.filter(**filter_kwargs)
