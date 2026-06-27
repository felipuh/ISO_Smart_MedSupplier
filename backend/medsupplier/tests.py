from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from datetime import date
from unittest.mock import patch
import inspect
from rest_framework.test import APIClient
from rest_framework import serializers as drf_serializers

from authentication.models import UserProfile
from core.models import Organization

from . import serializers as medsupplier_serializers
from .models import (
    EvidencePackage,
    EvidencePackageEntry,
    MedSupplierAuditEvent,
    MedSupplierESignature,
    MedSupplierUserScope,
    SupplierAccount,
    SupplierCAPA,
    SupplierDocument,
    SupplierFMEA,
    SupplierFMEAItem,
    SupplierPurchaseOrder,
    SupplierQualityEvent,
    SupplierQuote,
    SupplierQuoteLine,
    SupplierRFQ,
    SupplierScorecard,
)


class MedSupplierSerializerGuardrailTests(TestCase):
    def test_medsupplier_serializers_do_not_use_fields_all(self):
        for _, serializer_class in inspect.getmembers(medsupplier_serializers, inspect.isclass):
            if not issubclass(serializer_class, drf_serializers.ModelSerializer):
                continue
            meta = getattr(serializer_class, 'Meta', None)
            if not meta or not hasattr(meta, 'model'):
                continue
            fields = getattr(meta, 'fields', None)
            self.assertIsNotNone(fields, f'{serializer_class.__name__} must declare explicit fields.')
            self.assertNotEqual(fields, '__all__', f'{serializer_class.__name__} must not use fields=\"__all__\".')

    def test_private_commercial_field_catalog_covers_guardrail_terms(self):
        expected_private_fields = {
            'private_margin_notes',
            'supplier_cost',
            'margin',
            'commission',
            'advance',
            'internal_notes',
            'pricing_internal',
            'private_notes',
            'supplier_private_notes',
            'internal_cost',
            'internal_price',
            'forecast_private',
        }
        self.assertTrue(expected_private_fields.issubset(medsupplier_serializers.PRIVATE_COMMERCIAL_FIELDS))


class MedSupplierPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.auth_client = APIClient()
        self.auditor_client = APIClient()
        self.finance_client = APIClient()

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
        self.finance = user_model.objects.create_user(
            username='med_finance',
            email='med_finance@isosmart.local',
            password='StrongPass@123',
        )

        self.org_a = Organization.objects.create(name='Med Org A', slug='med-org-a', email='a@example.com')
        self.org_b = Organization.objects.create(name='Med Org B', slug='med-org-b', email='b@example.com')

        UserProfile.objects.create(user=self.manager, organization=self.org_a, role='iso_manager', is_active=True)
        UserProfile.objects.create(user=self.auditor, organization=self.org_a, role='auditor', is_active=True)
        UserProfile.objects.create(user=self.finance, organization=self.org_a, role='user', is_active=True)

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
        self.account_b_in_same_org = SupplierAccount.objects.create(
            organization=self.org_a,
            name='Unscoped Same Org Customer',
            account_code='MED-A-UNSCOPED',
            status='active',
            risk_level='low',
            visibility='customer_shared',
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
        self.finance_client.force_authenticate(user=self.finance)

        MedSupplierUserScope.objects.create(
            user=self.auditor,
            organization=self.org_a,
            account=self.account_a,
            side='customer',
            role='customer_auditor',
        )
        MedSupplierUserScope.objects.create(
            user=self.finance,
            organization=self.org_a,
            side='supplier',
            role='supplier_finance',
        )

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
            visibility='customer_shared',
            supplier_cost='600.00',
            margin='35.00',
            commission='50.00',
            advance='100.00',
            private_margin_notes='Internal margin note',
        )
        self.quote_line = SupplierQuoteLine.objects.create(
            organization=self.org_a,
            account=self.account_a,
            rfq=self.rfq,
            quote=self.quote,
            line_number=1,
            description='Regulated pouch line',
            quantity='10.000',
            unit_price='100.0000',
            supplier_cost='60.0000',
            margin='40.00',
            visibility='customer_shared',
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
            root_cause='Mismatch root cause.',
            corrective_action='Corrective action defined.',
            effectiveness_result='Effectiveness verified.',
            evidence_summary='Evidence attached in controlled package.',
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
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(response.data['results'][0]['account_code'], 'MED-A-001')

    def test_auditor_reads_only_shared_records(self):
        response = self.auditor_client.get(self.list_url, {'organization_id': self.org_a.id})
        self.assertEqual(response.status_code, 200)
        returned_codes = {item['account_code'] for item in response.data['results']}
        self.assertIn('MED-A-001', returned_codes)
        self.assertNotIn('MED-A-PRIVATE', returned_codes)
        self.assertNotIn('MED-A-UNSCOPED', returned_codes)

    def test_customer_quote_serializer_hides_private_commercial_fields(self):
        response = self.auditor_client.get(reverse('medsupplier-quote-list'), {'organization_id': self.org_a.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        quote_payload = response.data['results'][0]
        for field in ['private_margin_notes', 'supplier_cost', 'margin', 'commission', 'advance', 'internal_notes']:
            self.assertNotIn(field, quote_payload)
        self.assertEqual(quote_payload['quote_number'], 'Q-MED-A-001')

    def test_customer_cannot_access_private_cockpit(self):
        response = self.auditor_client.get(reverse('medsupplier-private-cockpit'), {'organization_id': self.org_a.id})
        self.assertEqual(response.status_code, 403)

    def test_supplier_finance_can_access_private_cockpit(self):
        response = self.finance_client.get(reverse('medsupplier-private-cockpit'), {'organization_id': self.org_a.id})
        self.assertEqual(response.status_code, 200)
        self.assertIn('finance', response.data)

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
            {'reason': 'Document release approved for controlled demo.'},
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
        self.assertTrue(MedSupplierESignature.objects.filter(object_id=str(self.document.id), meaning='approval').exists())

    def test_workflow_transitions_change_status(self):
        cases = [
            ('medsupplier-rfq-detail', self.rfq, 'send', 'sent'),
            ('medsupplier-quote-detail', self.quote, 'approve', 'approved'),
            ('medsupplier-purchase-order-detail', self.purchase_order, 'close', 'closed'),
            ('medsupplier-capa-detail', self.capa, 'close', 'closed'),
            ('medsupplier-quality-event-detail', self.quality_event, 'close', 'closed'),
        ]
        for route_name, instance, action_name, expected_status in cases:
            payload = {}
            if action_name in {'approve', 'close'}:
                payload['reason'] = f'{action_name} approved during workflow test.'
            response = self.auth_client.post(
                f"{reverse(route_name, args=[instance.id])}{action_name}/?organization_id={self.org_a.id}",
                payload,
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
            {'reason': 'Attempt obsolete approval.'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_expired_quote_cannot_be_approved(self):
        self.quote.valid_until = date(2020, 1, 1)
        self.quote.save(update_fields=['valid_until'])
        response = self.auth_client.post(
            f"{reverse('medsupplier-quote-detail', args=[self.quote.id])}approve/?organization_id={self.org_a.id}",
            {'reason': 'Attempt expired quote approval.'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_quality_event_with_open_capa_cannot_be_closed(self):
        response = self.auth_client.post(
            f"{reverse('medsupplier-quality-event-detail', args=[self.quality_event.id])}close/?organization_id={self.org_a.id}",
            {'reason': 'Attempt close with open CAPA.'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_capa_without_required_evidence_cannot_be_closed(self):
        self.capa.effectiveness_result = ''
        self.capa.evidence_summary = ''
        self.capa.save(update_fields=['effectiveness_result', 'evidence_summary'])
        response = self.auth_client.post(
            f"{reverse('medsupplier-capa-detail', args=[self.capa.id])}close/?organization_id={self.org_a.id}",
            {'reason': 'Attempt close incomplete CAPA.'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_quote_without_lines_cannot_be_approved(self):
        self.quote.lines.all().delete()
        response = self.auth_client.post(
            f"{reverse('medsupplier-quote-detail', args=[self.quote.id])}approve/?organization_id={self.org_a.id}",
            {'reason': 'Attempt approve quote without lines.'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_sensitive_action_requires_reason(self):
        response = self.auth_client.post(
            f"{reverse('medsupplier-quote-detail', args=[self.quote.id])}approve/?organization_id={self.org_a.id}",
            {},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('reason', response.data)

    def test_evidence_package_empty_cannot_be_approved_or_exported(self):
        package = EvidencePackage.objects.create(
            organization=self.org_a,
            account=self.account_a,
            package_number='EP-001',
            title='Empty package',
            visibility='regulated_evidence',
        )
        approve = self.auth_client.post(
            f"{reverse('medsupplier-evidence-package-detail', args=[package.id])}approve/?organization_id={self.org_a.id}",
            {'reason': 'Attempt approve empty package.'},
            format='json',
        )
        export = self.auth_client.get(
            f"{reverse('medsupplier-evidence-package-detail', args=[package.id])}export/?organization_id={self.org_a.id}",
        )
        self.assertEqual(approve.status_code, 400)
        self.assertEqual(export.status_code, 400)

    def test_evidence_package_with_entry_exports(self):
        package = EvidencePackage.objects.create(
            organization=self.org_a,
            account=self.account_a,
            package_number='EP-002',
            title='CAPA evidence',
            visibility='regulated_evidence',
        )
        EvidencePackageEntry.objects.create(
            package=package,
            object_type='suppliercapa',
            object_id=str(self.capa.id),
            label='CAPA evidence',
        )
        response = self.auth_client.get(
            f"{reverse('medsupplier-evidence-package-detail', args=[package.id])}export/?organization_id={self.org_a.id}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['package_number'], 'EP-002')

    def test_fmea_item_calculates_risk_score(self):
        fmea = SupplierFMEA.objects.create(
            organization=self.org_a,
            account=self.account_a,
            fmea_number='FMEA-001',
            title='Process FMEA',
            visibility='customer_shared',
        )
        item = SupplierFMEAItem.objects.create(
            organization=self.org_a,
            account=self.account_a,
            fmea=fmea,
            hazard='Seal failure',
            failure_mode='Incomplete seal',
            severity=4,
            occurrence=3,
            detection=2,
            visibility='customer_shared',
        )
        self.assertEqual(item.risk_score, 24)

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
        self.assertEqual(response.data['accounts'], 3)
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
