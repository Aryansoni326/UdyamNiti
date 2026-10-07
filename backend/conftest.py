"""
Global Pytest Deterministic Fixtures for UdyamNiti Backend.
Provides hermetic test state, pre-seeded synthetic policies,
canonical enterprise profile (ABC Engineering Works), and isolated API clients.
"""
import pytest
from datetime import date
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.accounts.models import UserSecurityProfile, UserRole
from apps.business_profiles.models import BusinessProfile, BusinessGoal
from apps.policies.models import Scheme, SchemeVersion, SchemeRule, SchemeBenefit, SchemePrerequisite
from apps.relationships.models import SchemeRelationship
from apps.rag.models import PolicySourceDocument, PolicyDocumentChunk
from apps.documents.models import BusinessDocument


@pytest.fixture
def api_client():
    """Unauthenticated DRF API client."""
    return APIClient()


@pytest.fixture
def abc_engineering_user(db):
    """Canonical demo user representing ABC Engineering Works."""
    user, _ = User.objects.get_or_create(
        username='abc_engineering',
        defaults={
            'email': 'info@abcengineering.in',
            'first_name': 'Rajesh',
            'last_name': 'Patel'
        }
    )
    user.set_password('demo1234')
    user.save()
    UserSecurityProfile.objects.get_or_create(
        user=user,
        defaults={'role': UserRole.MSME_USER}
    )
    return user


@pytest.fixture
def competitor_user(db):
    """Separate tenant user for multi-tenant isolation testing."""
    user, _ = User.objects.get_or_create(
        username='competitor_tenant',
        defaults={
            'email': 'competitor@separate-tenant.in',
            'first_name': 'Vikram',
            'last_name': 'Shah'
        }
    )
    user.set_password('competitor1234')
    user.save()
    UserSecurityProfile.objects.get_or_create(
        user=user,
        defaults={'role': UserRole.MSME_USER}
    )
    return user


@pytest.fixture
def admin_user(db):
    """Privileged policy analyst / system admin user."""
    user, _ = User.objects.get_or_create(
        username='policy_analyst_admin',
        defaults={
            'email': 'analyst@udyamniti.gov.in',
            'is_staff': True,
            'is_superuser': True
        }
    )
    user.set_password('admin1234')
    user.save()
    UserSecurityProfile.objects.get_or_create(
        user=user,
        defaults={'role': UserRole.SYSTEM_ADMIN}
    )
    return user


@pytest.fixture
def authenticated_client(abc_engineering_user):
    """API Client pre-authenticated as ABC Engineering."""
    client = APIClient()
    client.force_authenticate(user=abc_engineering_user)
    return client


@pytest.fixture
def abc_engineering_profile(db, abc_engineering_user):
    """
    Deterministic golden profile for ABC Engineering Works.
    Small enterprise, manufacturing CNC machining, Gujarat, ₹2.10 Cr turnover.
    """
    profile, _ = BusinessProfile.objects.update_or_create(
        udyam_registration_number='UDYAM-GJ-29-0012345',
        defaults={
            'user': abc_engineering_user,
            'business_name': 'ABC Engineering Works',
            'gstin': '24AADCA1234F1Z5',
            'pan': 'AADCA1234F',
            'msme_category': 'small',
            'enterprise_category': 'small',
            'entity_type': 'proprietorship',
            'industry_sector': 'Precision Engineering & Metal Fabrication',
            'is_manufacturing': True,
            'is_service': False,
            'state': 'Gujarat',
            'district': 'Surat',
            'annual_turnover': 210.0,
            'annual_turnover_lakhs': 210.0,
            'investment_in_plant_machinery_lakhs': 45.0,
            'years_in_operation': 8,
            'total_employees': 22,
            'has_bank_account': True,
            'is_npa': False,
            'has_iso_certification': False,  # Unlockable prerequisite!
            'uses_digital_payments': True,
        }
    )
    return profile


@pytest.fixture
def competitor_profile(db, competitor_user):
    """Isolated profile belonging to competitor user."""
    profile, _ = BusinessProfile.objects.update_or_create(
        udyam_registration_number='UDYAM-MH-12-0098765',
        defaults={
            'user': competitor_user,
            'business_name': 'Competitor Aerospace Tools',
            'gstin': '27XYZAB9876C1Z1',
            'msme_category': 'medium',
            'enterprise_category': 'medium',
            'state': 'Maharashtra',
            'annual_turnover': 550.0,
            'annual_turnover_lakhs': 550.0
        }
    )
    return profile


@pytest.fixture
def synthetic_schemes(db):
    """
    Pre-seeded synthetic schemes with complete deterministic rule trees,
    financial thresholds, benefits, and prerequisites.
    """
    # 1. CLCSS (Credit Linked Capital Subsidy Scheme)
    s1, _ = Scheme.objects.get_or_create(
        scheme_code='CLCSS',
        defaults={
            'name': 'Credit Linked Capital Subsidy Scheme for Technology Upgradation',
            'short_name': 'CLCSS',
            'ministry_department': 'Ministry of MSME',
            'level': 'central',
            'support_type': 'capital_subsidy',
            'target_msme_categories': ['micro', 'small'],
            'target_states': [],
            'max_benefit_amount_lakhs': 15.0,
            'benefit_percentage': 15.0,
            'status': 'active',
            'official_portal_url': 'https://msme.gov.in/clcss',
            'description': '15% upfront capital subsidy on institutional credit up to ₹100 lakh for technology upgradation.',
            'eligibility_summary': 'Micro and Small manufacturing enterprises only. Medium enterprises excluded.'
        }
    )

    # CLCSS Rules
    SchemeRule.objects.update_or_create(
        scheme=s1,
        rule_name='MSME Category — Micro or Small only',
        defaults={
            'field_path': 'msme_category',
            'operator': 'in',
            'expected_value': ['micro', 'small'],
            'importance': 'mandatory',
            'source_clause': 'Only Micro and Small enterprises are eligible.',
            'display_label': 'Enterprise Category',
            'is_active': True
        }
    )
    SchemeRule.objects.update_or_create(
        scheme=s1,
        rule_name='Manufacturing Sector',
        defaults={
            'field_path': 'is_manufacturing',
            'operator': 'bool_true',
            'expected_value': True,
            'importance': 'mandatory',
            'source_clause': 'Covers manufacturing sector MSEs.',
            'display_label': 'Manufacturing Sector',
            'is_active': True
        }
    )
    SchemeRule.objects.update_or_create(
        scheme=s1,
        rule_name='Not NPA',
        defaults={
            'field_path': 'is_npa',
            'operator': 'bool_false',
            'expected_value': False,
            'importance': 'mandatory',
            'source_clause': 'Unit must not be classified as NPA.',
            'display_label': 'Not NPA',
            'is_active': True
        }
    )

    # 2. CGTMSE (Credit Guarantee Scheme)
    s2, _ = Scheme.objects.get_or_create(
        scheme_code='CGTMSE',
        defaults={
            'name': 'Credit Guarantee Fund Trust for Micro and Small Enterprises',
            'short_name': 'CGTMSE',
            'ministry_department': 'Ministry of MSME / SIDBI',
            'level': 'central',
            'support_type': 'credit_guarantee',
            'target_msme_categories': ['micro', 'small'],
            'target_states': [],
            'max_benefit_amount_lakhs': 200.0,
            'benefit_percentage': 85.0,
            'status': 'active',
            'official_portal_url': 'https://cgtmse.in',
            'description': 'Collateral-free credit facility up to ₹200 lakh for MSEs.',
            'eligibility_summary': 'New and existing MSEs engaged in manufacturing or service.'
        }
    )

    # 3. Gujarat Capital Investment Subsidy (Atmanirbhar Gujarat)
    s3, _ = Scheme.objects.get_or_create(
        scheme_code='GUJ_IND_SUBSIDY',
        defaults={
            'name': 'Gujarat Industrial Policy — Capital Subsidy for MSMEs',
            'short_name': 'Gujarat Capital Subsidy',
            'ministry_department': 'Industries and Mines Department, Gujarat',
            'level': 'state_gujarat',
            'support_type': 'capital_subsidy',
            'target_msme_categories': ['micro', 'small', 'medium'],
            'target_states': ['Gujarat'],
            'max_benefit_amount_lakhs': 35.0,
            'benefit_percentage': 12.0,
            'status': 'active',
            'official_portal_url': 'https://ifp.gujarat.gov.in',
            'description': '12% capital investment subsidy for plant & machinery in Gujarat.',
            'eligibility_summary': 'MSME units situated and registered in Gujarat.'
        }
    )
    SchemeRule.objects.update_or_create(
        scheme=s3,
        rule_name='Location in Gujarat',
        defaults={
            'field_path': 'state',
            'operator': 'eq',
            'expected_value': 'Gujarat',
            'importance': 'mandatory',
            'source_clause': 'Unit must be established in the state of Gujarat.',
            'display_label': 'State Location',
            'is_active': True
        }
    )

    # 4. ZED Scheme (Prerequisite test: requires ISO/ZED certification)
    s4, _ = Scheme.objects.get_or_create(
        scheme_code='ZED_CERT',
        defaults={
            'name': 'MSME Sustainable (ZED) Certification Scheme',
            'short_name': 'ZED',
            'ministry_department': 'Ministry of MSME',
            'level': 'central',
            'support_type': 'certification',
            'target_msme_categories': ['micro', 'small', 'medium'],
            'max_benefit_amount_lakhs': 5.0,
            'status': 'active',
            'official_portal_url': 'https://zed.msme.gov.in',
            'description': 'Subsidies up to 80% on ZED certification assessment.'
        }
    )
    SchemePrerequisite.objects.update_or_create(
        scheme=s4,
        prerequisite_type='certification',
        title='ISO 9001 or ZED Bronze Certification',
        defaults={
            'description': 'Enterprise must register on ZED portal and achieve Bronze level.',
            'how_to_satisfy': 'Submit online self-assessment on zed.msme.gov.in',
            'is_hard_prerequisite': False
        }
    )

    return {
        'CLCSS': s1,
        'CGTMSE': s2,
        'GUJ_IND_SUBSIDY': s3,
        'ZED_CERT': s4
    }


@pytest.fixture
def synthetic_relationships(db, synthetic_schemes):
    """Pre-seeds cross-scheme compatibility and stacking relationships."""
    clcss = synthetic_schemes['CLCSS']
    cgtmse = synthetic_schemes['CGTMSE']
    guj_sub = synthetic_schemes['GUJ_IND_SUBSIDY']

    rel1, _ = SchemeRelationship.objects.update_or_create(
        scheme_a=clcss,
        scheme_b=cgtmse,
        defaults={
            'relationship_type': 'synergistic',
            'description': 'CLCSS provides capital subsidy while CGTMSE guarantees the loan on the same CNC machine purchase.',
            'source_evidence': 'Central MSME Credit Guidelines Clause 6.'
        }
    )
    rel2, _ = SchemeRelationship.objects.update_or_create(
        scheme_a=clcss,
        scheme_b=guj_sub,
        defaults={
            'relationship_type': 'compatible',
            'description': 'Central 15% subsidy and Gujarat 12% state subsidy can be stacked up to statutory project limits.',
            'source_evidence': 'Gujarat Industrial Policy 2020 Clause 4.2.'
        }
    )
    return [rel1, rel2]


@pytest.fixture
def golden_demo_goal(db, abc_engineering_profile):
    """Canonical CNC machine investment goal for ABC Engineering."""
    goal, _ = BusinessGoal.objects.update_or_create(
        business_profile=abc_engineering_profile,
        defaults={
            'raw_goal_text': 'I want to purchase a ₹50 lakh CNC machine to expand our precision machining capacity.',
            'parsed_objective': 'Purchase CNC machine for precision machining expansion',
            'parsed_project_type': 'machinery_purchase',
            'parsed_investment_amount_lakhs': 50.0,
            'parsed_support_categories': ['capital_subsidy', 'credit_guarantee'],
            'parsed_industry_hints': ['manufacturing', 'precision engineering', 'cnc machining'],
            'status': 'ready'
        }
    )
    return goal
