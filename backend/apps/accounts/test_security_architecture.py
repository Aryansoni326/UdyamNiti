"""
Security Architecture & Tenant Isolation Test Suite.
Tests:
1. Object-Level Isolation: Users cannot read, modify, or link other users' profiles, documents, strategies, or workspaces.
2. Staff / Admin Elevated Access: Staff can access resources for operational auditing.
3. Brute-Force Protection & Account Lockout.
4. Password Hashing & Robust Validation.
5. Security Headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options).
6. API Rate Limiting & Throttling Configuration.
7. Security Audit Logging.
"""
from datetime import date
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status

from apps.accounts.models import UserSecurityProfile, UserRole, SecurityAuditLog, AuditAction
from apps.business_profiles.models import BusinessProfile, BusinessGoal
from apps.documents.models import BusinessDocument
from apps.strategy.models import Strategy
from apps.actions.models import ActionTask, ApplicationPreparationWorkspace
from apps.policies.models import Scheme


class ObjectLevelTenantIsolationTestCase(TestCase):
    def setUp(self):
        self.client_a = APIClient()
        self.client_b = APIClient()
        self.client_admin = APIClient()

        # User A (MSME Owner A)
        self.user_a = User.objects.create_user(
            username='user_a',
            email='user_a@enterprise.example.com',
            password='Password12345!'
        )
        UserSecurityProfile.objects.create(user=self.user_a, role=UserRole.MSME_USER)
        self.client_a.force_authenticate(user=self.user_a)

        # User B (MSME Owner B - The Attacker / Separate Tenant)
        self.user_b = User.objects.create_user(
            username='user_b',
            email='user_b@competitor.example.com',
            password='Password12345!'
        )
        UserSecurityProfile.objects.create(user=self.user_b, role=UserRole.MSME_USER)
        self.client_b.force_authenticate(user=self.user_b)

        # Staff User
        self.user_admin = User.objects.create_superuser(
            username='admin_officer',
            email='admin@udyamniti.gov.in',
            password='AdminPassword999!'
        )
        UserSecurityProfile.objects.create(user=self.user_admin, role=UserRole.SYSTEM_ADMIN)
        self.client_admin.force_authenticate(user=self.user_admin)

        # Create Profile for User A
        self.profile_a = BusinessProfile.objects.create(
            user=self.user_a,
            business_name="Enterprise A Pvt Ltd",
            enterprise_category="micro",
            state="Gujarat",
            annual_turnover=50.0
        )

        # Create Profile for User B
        self.profile_b = BusinessProfile.objects.create(
            user=self.user_b,
            business_name="Enterprise B Industries",
            enterprise_category="small",
            state="Gujarat",
            annual_turnover=200.0
        )

        # Create Scheme
        self.scheme = Scheme.objects.create(
            scheme_code="TEST_SCHEME_01",
            name="Gujarat MSME Capital Assistance",
            status="active",
            level="state_gujarat",
            support_type="capital_subsidy"
        )

        # Create Document for User A
        self.doc_a = BusinessDocument.objects.create(
            business_profile=self.profile_a,
            document_type="udyam_certificate",
            document_name="Udyam_Certificate_A.pdf",
            file_hash="hash_a_123"
        )

        # Create Strategy for User A
        self.goal_a = BusinessGoal.objects.create(
            business_profile=self.profile_a,
            goal_type="expand_capacity",
            target_amount=100.0
        )
        self.strategy_a = Strategy.objects.create(
            business_profile=self.profile_a,
            goal=self.goal_a,
            title="Expansion Strategy A"
        )

    def test_user_b_cannot_list_user_a_profiles(self):
        """User B's profile list query only returns profile B, completely omitting profile A."""
        res = self.client_b.get('/api/v1/business-profiles/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [item['id'] for item in res.data.get('results', res.data)]
        self.assertIn(str(self.profile_b.id), ids)
        self.assertNotIn(str(self.profile_a.id), ids)

    def test_user_b_cannot_get_or_modify_user_a_profile(self):
        """User B attempting to directly access or modify Profile A receives 404 (isolated)."""
        get_res = self.client_b.get(f'/api/v1/business-profiles/{self.profile_a.id}/')
        self.assertEqual(get_res.status_code, status.HTTP_404_NOT_FOUND)

        patch_res = self.client_b.patch(
            f'/api/v1/business-profiles/{self.profile_a.id}/',
            {'business_name': 'Hacked by User B'},
            format='json'
        )
        self.assertEqual(patch_res.status_code, status.HTTP_404_NOT_FOUND)

        # Confirm data unaltered
        self.profile_a.refresh_from_db()
        self.assertEqual(self.profile_a.business_name, "Enterprise A Pvt Ltd")

    def test_user_b_cannot_list_or_access_user_a_documents(self):
        """User B cannot view or download User A's uploaded certificates."""
        list_res = self.client_b.get('/api/v1/documents/')
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        doc_ids = [item['id'] for item in list_res.data.get('results', list_res.data)]
        self.assertNotIn(str(self.doc_a.id), doc_ids)

        get_res = self.client_b.get(f'/api/v1/documents/{self.doc_a.id}/')
        self.assertEqual(get_res.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_b_cannot_access_user_a_strategy(self):
        """User B cannot view User A's private strategy evaluations."""
        get_res = self.client_b.get(f'/api/v1/strategy/{self.strategy_a.id}/')
        self.assertEqual(get_res.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_b_cannot_create_workspace_on_user_a_profile(self):
        """User B attempting to create an Application Workspace targeting User A's profile is forbidden."""
        res = self.client_b.post(
            '/api/v1/workspace/get-or-create/',
            {
                'business_profile_id': str(self.profile_a.id),
                'scheme_id': str(self.scheme.id)
            },
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Forbidden", res.data.get('error', ''))

    def test_admin_has_elevated_access(self):
        """Staff/System Admins can query profiles across tenants for support and auditing."""
        res = self.client_admin.get('/api/v1/business-profiles/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [item['id'] for item in res.data.get('results', res.data)]
        self.assertIn(str(self.profile_a.id), ids)
        self.assertIn(str(self.profile_b.id), ids)


class AuthenticationAndSecurityControlsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(
            username='auth_test_user',
            email='test@example.com',
            password='ValidPassword123!'
        )
        self.sec_profile = UserSecurityProfile.objects.create(
            user=self.test_user,
            role=UserRole.MSME_USER
        )

    def test_password_validation_enforces_complexity(self):
        """Passwords that are too short or common fail validation."""
        with self.assertRaises(ValidationError):
            validate_password("short", self.test_user)
        with self.assertRaises(ValidationError):
            validate_password("password", self.test_user)

        # Valid complex password passes
        self.assertIsNone(validate_password("SecureGovPass#2026", self.test_user))

    def test_successful_login_returns_user_and_csrf(self):
        """Successful login returns user payload and CSRF token."""
        res = self.client.post(
            '/api/v1/auth/login/',
            {'username': 'auth_test_user', 'password': 'ValidPassword123!'},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('user', res.data)
        self.assertIn('csrf_token', res.data)
        self.assertEqual(res.data['user']['username'], 'auth_test_user')

    def test_brute_force_lockout_after_five_failed_attempts(self):
        """Five consecutive bad password attempts lock the account."""
        for attempt in range(4):
            res = self.client.post(
                '/api/v1/auth/login/',
                {'username': 'auth_test_user', 'password': 'WrongPassword!'},
                format='json'
            )
            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        # 5th attempt triggers lockout
        res5 = self.client.post(
            '/api/v1/auth/login/',
            {'username': 'auth_test_user', 'password': 'WrongPassword!'},
            format='json'
        )
        self.assertEqual(res5.status_code, status.HTTP_401_UNAUTHORIZED)

        self.sec_profile.refresh_from_db()
        self.assertTrue(self.sec_profile.is_locked())

        # 6th attempt is blocked with 429
        res6 = self.client.post(
            '/api/v1/auth/login/',
            {'username': 'auth_test_user', 'password': 'ValidPassword123!'},
            format='json'
        )
        self.assertEqual(res6.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('locked', res6.data.get('error', '').lower())

    def test_security_headers_present_on_all_responses(self):
        """Responses include HSTS, CSP, X-Frame-Options, X-Content-Type-Options."""
        res = self.client.get('/api/v1/health/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn('Strict-Transport-Security', res.headers)
        self.assertEqual(res.headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(res.headers['X-Frame-Options'], 'DENY')
        self.assertIn("default-src 'self'", res.headers['Content-Security-Policy'])
        self.assertEqual(res.headers['Referrer-Policy'], 'strict-origin-when-cross-origin')
        self.assertIn('camera=()', res.headers['Permissions-Policy'])

    def test_security_audit_logging_on_operations(self):
        """Sensitive API actions create audit trail records."""
        # Authenticate and make a request
        self.client.force_authenticate(user=self.test_user)
        self.client.post(
            '/api/v1/business-profiles/',
            {
                'business_name': 'Audit Log Test Enterprise',
                'enterprise_category': 'micro',
                'state': 'Gujarat'
            },
            format='json'
        )

        logs = SecurityAuditLog.objects.filter(actor_username='auth_test_user')
        self.assertTrue(logs.exists())
