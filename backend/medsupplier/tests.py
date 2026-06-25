from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from rest_framework.test import APIClient

from authentication.models import UserProfile
from core.models import Organization

from .models import SupplierAccount


class MedSupplierPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.auth_client = APIClient()
        self.auditor_client = APIClient()

        user_model = get_user_model()
        self.manager = user_model.objects.create_user(
            username='med_manager',
            email='med_manager@isosmart.local',
            password='StrongPass@123',
        )
        self.auditor = user_model.objects.create_user(
            username='med_auditor',
            email='med_auditor@isosmart.local',
            password='StrongPass@123',
        )

        self.org_a = Organization.objects.create(name='Med Org A', slug='med-org-a', email='a@example.com')
        self.org_b = Organization.objects.create(name='Med Org B', slug='med-org-b', email='b@example.com')

        UserProfile.objects.create(user=self.manager, organization=self.org_a, role='iso_manager', is_active=True)
        UserProfile.objects.create(user=self.auditor, organization=self.org_a, role='auditor', is_active=True)

        self.account_a = SupplierAccount.objects.create(
            organization=self.org_a,
            name='Cardio Packaging Customer',
            account_code='MED-A-001',
            status='active',
            risk_level='medium',
        )
        SupplierAccount.objects.create(
            organization=self.org_b,
            name='Foreign Customer',
            account_code='MED-B-001',
            status='active',
            risk_level='high',
        )

        self.auth_client.force_authenticate(user=self.manager)
        self.auditor_client.force_authenticate(user=self.auditor)

        self.list_url = reverse('medsupplier-account-list')
        self.summary_url = reverse('medsupplier-dashboard-summary')
        self.integration_status_url = reverse('medsupplier-integration-status')

    def test_accounts_require_authentication(self):
        response = self.client.get(self.list_url, {'organization_id': self.org_a.id})
        self.assertEqual(response.status_code, 401)

    def test_accounts_require_organization_scope(self):
        response = self.auth_client.get(self.list_url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('organization_id', response.data)

    def test_accounts_block_foreign_organization(self):
        response = self.auth_client.get(self.list_url, {'organization_id': self.org_b.id})
        self.assertEqual(response.status_code, 403)

    def test_accounts_return_only_active_organization_data(self):
        response = self.auth_client.get(self.list_url, {'organization_id': self.org_a.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['account_code'], 'MED-A-001')

    def test_manager_can_create_account_inside_organization(self):
        response = self.auth_client.post(
            f'{self.list_url}?organization_id={self.org_a.id}',
            {
                'name': 'Neuro Labels Customer',
                'account_code': 'MED-A-002',
                'status': 'prospect',
                'risk_level': 'low',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['organization'], self.org_a.id)

    def test_auditor_cannot_create_account(self):
        response = self.auditor_client.post(
            f'{self.list_url}?organization_id={self.org_a.id}',
            {
                'name': 'Read Only Customer',
                'account_code': 'MED-A-003',
                'status': 'prospect',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_dashboard_summary_is_scoped(self):
        response = self.auth_client.get(self.summary_url, {'organization_id': self.org_a.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['product'], 'ISO Smart MedSupplier')
        self.assertEqual(response.data['accounts'], 1)
        self.assertEqual(response.data['organization_id'], self.org_a.id)

    @patch('medsupplier.views.admin_apps_client')
    def test_integration_status_declares_adminapps_as_authority(self, mocked_adminapps):
        mocked_adminapps.health_check.return_value = {'status': 'ok'}
        mocked_adminapps.get_organization_modules.return_value = {
            'modules': [{'code': 'MEDSUPPLIER', 'name': 'MedSupplier', 'enabled': True}],
            'source': 'adminapps',
        }

        response = self.auth_client.get(self.integration_status_url, {'organization_id': self.org_a.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['module_code'], 'MEDSUPPLIER')
        self.assertTrue(response.data['adminapps_authority']['organizations'])
        self.assertTrue(response.data['adminapps_authority']['users'])
        self.assertTrue(response.data['entitlement']['enabled'])
