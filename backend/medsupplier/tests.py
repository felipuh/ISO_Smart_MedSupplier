from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from datetime import date
from unittest.mock import patch
from rest_framework.test import APIClient

from authentication.models import UserProfile
from core.models import Organization

from .models import (
    MedSupplierAuditEvent,
    SupplierAccount,
    SupplierCAPA,
    SupplierDocument,
    SupplierPurchaseOrder,
    SupplierQualityEvent,
    SupplierQuote,
    SupplierRFQ,
    SupplierScorecard,
)


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
        self.private_account = SupplierAccount.objects.create(
            organization=self.org_a,
            name='Private Pipeline Account',
            account_code='MED-A-PRIVATE',
            status='prospect',
            risk_level='high',
            visibility='private',
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

        self.document = SupplierDocument.objects.create(
            organization=self.org_a,
            account=self.account_a,
            document_number='DOC-MED-A-001',
            title='COC Template',
            document_type='COC',
            status='draft',
        )
        self.rfq = SupplierRFQ.objects.create(
            organization=self.org_a,
            account=self.account_a,
            rfq_number='RFQ-MED-A-001',
            title='Pilot packaging run',
            status='draft',
        )
        self.quote = SupplierQuote.objects.create(
            organization=self.org_a,
            account=self.account_a,
            rfq=self.rfq,
            quote_number='Q-MED-A-001',
            status='submitted',
        )
        self.purchase_order = SupplierPurchaseOrder.objects.create(
            organization=self.org_a,
            account=self.account_a,
            quote=self.quote,
            po_number='PO-MED-A-001',
            status='in_production',
        )
        self.quality_event = SupplierQualityEvent.objects.create(
            organization=self.org_a,
            account=self.account_a,
            event_number='NCR-MED-A-001',
            event_type='ncr',
            status='capa_required',
            title='Label mismatch',
            description='Label revision mismatch.',
        )
        self.capa = SupplierCAPA.objects.create(
            organization=self.org_a,
            account=self.account_a,
            quality_event=self.quality_event,
            capa_number='CAPA-MED-A-001',
            status='effectiveness_check',
            effectiveness_result='Effectiveness verified.',
        )

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
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['account_code'], 'MED-A-001')

    def test_auditor_reads_only_shared_records(self):
        response = self.auditor_client.get(self.list_url, {'organization_id': self.org_a.id})
        self.assertEqual(response.status_code, 200)
        returned_codes = {item['account_code'] for item in response.data['results']}
        self.assertIn('MED-A-001', returned_codes)
        self.assertNotIn('MED-A-PRIVATE', returned_codes)

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
        self.assertTrue(
            MedSupplierAuditEvent.objects.filter(
                organization=self.org_a,
                action='create',
                record_type='supplieraccount',
                record_id=str(response.data['id']),
            ).exists()
        )

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

    def test_document_approve_changes_status_and_audits(self):
        response = self.auth_client.post(
            f"{reverse('medsupplier-document-detail', args=[self.document.id])}approve/?organization_id={self.org_a.id}",
            {},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.document.refresh_from_db()
        self.assertEqual(self.document.status, 'effective')
        self.assertTrue(
            MedSupplierAuditEvent.objects.filter(
                organization=self.org_a,
                action='status_change',
                record_type='supplierdocument',
                record_id=str(self.document.id),
            ).exists()
        )

    def test_workflow_transitions_change_status(self):
        cases = [
            ('medsupplier-rfq-detail', self.rfq, 'send', 'sent'),
            ('medsupplier-quote-detail', self.quote, 'approve', 'approved'),
            ('medsupplier-purchase-order-detail', self.purchase_order, 'close', 'closed'),
            ('medsupplier-capa-detail', self.capa, 'close', 'closed'),
            ('medsupplier-quality-event-detail', self.quality_event, 'close', 'closed'),
        ]
        for route_name, instance, action_name, expected_status in cases:
            response = self.auth_client.post(
                f"{reverse(route_name, args=[instance.id])}{action_name}/?organization_id={self.org_a.id}",
                {},
                format='json',
            )
            self.assertEqual(response.status_code, 200)
            instance.refresh_from_db()
            self.assertEqual(instance.status, expected_status)

    def test_obsolete_document_cannot_be_approved(self):
        self.document.status = 'obsolete'
        self.document.save(update_fields=['status'])
        response = self.auth_client.post(
            f"{reverse('medsupplier-document-detail', args=[self.document.id])}approve/?organization_id={self.org_a.id}",
            {},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_expired_quote_cannot_be_approved(self):
        self.quote.valid_until = date(2020, 1, 1)
        self.quote.save(update_fields=['valid_until'])
        response = self.auth_client.post(
            f"{reverse('medsupplier-quote-detail', args=[self.quote.id])}approve/?organization_id={self.org_a.id}",
            {},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_quality_event_with_open_capa_cannot_be_closed(self):
        response = self.auth_client.post(
            f"{reverse('medsupplier-quality-event-detail', args=[self.quality_event.id])}close/?organization_id={self.org_a.id}",
            {},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_capa_without_effectiveness_result_cannot_be_closed(self):
        self.capa.effectiveness_result = ''
        self.capa.save(update_fields=['effectiveness_result'])
        response = self.auth_client.post(
            f"{reverse('medsupplier-capa-detail', args=[self.capa.id])}close/?organization_id={self.org_a.id}",
            {},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_generate_qbr_creates_scorecard_and_audit_event(self):
        response = self.auth_client.post(
            f"{reverse('medsupplier-account-detail', args=[self.account_a.id])}generate-qbr/?organization_id={self.org_a.id}",
            {
                'period_start': '2026-06-01',
                'period_end': '2026-06-30',
                'quality_score': '90',
                'delivery_score': '95',
                'responsiveness_score': '92',
                'overall_score': '92.33',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        scorecard = SupplierScorecard.objects.get(account=self.account_a, period_start='2026-06-01')
        self.assertEqual(str(scorecard.overall_score), '92.33')
        self.assertTrue(
            MedSupplierAuditEvent.objects.filter(
                organization=self.org_a,
                action='create',
                record_type='supplierscorecard',
                record_id=str(scorecard.id),
            ).exists()
        )

    def test_dashboard_summary_is_scoped(self):
        response = self.auth_client.get(self.summary_url, {'organization_id': self.org_a.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['product'], 'ISO Smart MedSupplier')
        self.assertEqual(response.data['accounts'], 2)
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
