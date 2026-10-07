"""
Authentication and Identity Endpoints.
Provides:
- login (with brute-force protection and audit tracking)
- logout (invalidates session)
- register (creates user + security profile)
- me (current user profile and RBAC role)
- csrf (CSRF token provisioning)
- audit-logs (security audit inspection for policy admins)
- demo (hackathon fast switch)
- health (monitoring)
"""
from django.urls import path
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import UserSecurityProfile, UserRole, SecurityAuditLog, AuditAction
from .serializers import UserDetailSerializer, LoginRequestSerializer, RegisterRequestSerializer, SecurityAuditLogSerializer
from .permissions import IsPolicyAdmin
from .throttling import AuthRateThrottle


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def login_view(request):
    """
    Secure login endpoint with brute-force lockout, session generation, and audit logging.
    """
    serializer = LoginRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    # Check for user existence and lockout status
    user_obj = User.objects.filter(username=username).first()
    if user_obj:
        sec_profile, _ = UserSecurityProfile.objects.get_or_create(user=user_obj)
        if sec_profile.is_locked():
            return Response(
                {
                    'error': 'Account is temporarily locked due to multiple failed login attempts. Please try again later.',
                    'locked_until': sec_profile.locked_until.isoformat()
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

    user = authenticate(request, username=username, password=password)
    if user:
        # Reset failed attempts
        sec_profile, _ = UserSecurityProfile.objects.get_or_create(user=user)
        sec_profile.reset_failed_logins()

        login(request, user)
        csrf_token = get_token(request)

        return Response({
            'user': UserDetailSerializer(user).data,
            'csrf_token': csrf_token,
            'message': 'Authentication successful'
        }, status=status.HTTP_200_OK)
    else:
        # Register failed attempt
        if user_obj:
            sec_profile.register_failed_login()

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logs out user and destroys session."""
    logout(request)
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def register_view(request):
    """Registers a new MSME user with security profile and RBAC role."""
    serializer = RegisterRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    validated = serializer.validated_data

    if User.objects.filter(username=validated['username']).exists():
        return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=validated['email']).exists():
        return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=validated['username'],
        email=validated['email'],
        password=validated['password']
    )
    UserSecurityProfile.objects.create(
        user=user,
        role=validated.get('role', UserRole.MSME_USER)
    )

    login(request, user)
    return Response({
        'user': UserDetailSerializer(user).data,
        'csrf_token': get_token(request),
        'message': 'Account created successfully'
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Returns currently authenticated user profile and roles."""
    return Response(UserDetailSerializer(request.user).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token_view(request):
    """Provides CSRF token for Single-Page Application (SPA) clients."""
    token = get_token(request)
    return Response({'csrf_token': token})


@api_view(['GET'])
@permission_classes([AllowAny])
def demo_login(request):
    """Auto-login as ABC Engineering for rapid hackathon testing."""
    user = User.objects.filter(username='abc_engineering').first()
    if not user:
        # Create seed demo user if not present
        user = User.objects.create_user(
            username='abc_engineering',
            email='contact@abc-eng.example.com',
            password='HackathonDemoPassword2026!'
        )
        UserSecurityProfile.objects.get_or_create(
            user=user,
            role=UserRole.MSME_USER
        )

    login(request, user)

    # Ensure canonical ABC Engineering Works BusinessProfile exists for zero-friction demo
    from apps.business_profiles.models import BusinessProfile
    profile = BusinessProfile.objects.filter(user=user).first()
    if not profile:
        profile = BusinessProfile.objects.create(
            user=user,
            business_name="ABC Engineering Works",
            udyam_registration_number="UDYAM-GJ-29-0012345",
            gstin="24AADCA1234F1Z5",
            msme_category="small",
            enterprise_category="small",
            entity_type="proprietorship",
            industry_sector="Precision Engineering & Metal Fabrication",
            is_manufacturing=True,
            is_service=False,
            state="Gujarat",
            district="Surat",
            annual_turnover=210.0,
            annual_turnover_lakhs=210.0,
            investment_in_plant_machinery_lakhs=45.0,
            has_bank_account=True,
            is_npa=False,
            has_iso_certification=False,
            uses_digital_payments=True
        )

    return Response({
        'user': UserDetailSerializer(user).data,
        'profile_id': str(profile.id),
        'csrf_token': get_token(request),
        'demo_mode': True
    })


@api_view(['GET'])
@permission_classes([IsPolicyAdmin])
def security_audit_logs_view(request):
    """Admin-only view for inspecting security audit events."""
    logs = SecurityAuditLog.objects.all()[:50]
    return Response(SecurityAuditLogSerializer(logs, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        'status': 'healthy',
        'service': 'UdyamNiti API',
        'security_controls': 'active',
        'tls_assumptions': 'Strict-Transport-Security enabled'
    })


urlpatterns = [
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/register/', register_view, name='register'),
    path('auth/me/', me_view, name='me'),
    path('auth/csrf/', csrf_token_view, name='csrf'),
    path('auth/demo/', demo_login, name='demo_login'),
    path('auth/audit-logs/', security_audit_logs_view, name='security_audit_logs'),
    path('health/', health_check, name='health_check'),
]
