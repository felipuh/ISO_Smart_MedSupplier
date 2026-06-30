from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse
from datetime import date, timedelta
from unittest.mock import patch
import inspect
from io import StringIO
from rest_framework.test import APIClient
from rest_framework import serializers as drf_serializers

from authentication.models import UserProfile
from core.models import Organization
from integration.client import AdminAppsClient

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
    SupplierDocumentVersion,
    SupplierFMEA,
    SupplierFMEAItem,
    SupplierInspection,
    SupplierLot,
    SupplierOrderLine,
    SupplierPurchaseOrder,
    SupplierQualityEvent,
    SupplierQuote,
    SupplierQuoteLine,
    SupplierRFQ,
    SupplierScorecard,
    SupplierShipment,
    SupplierShipmentMilestone,
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
        self.assertIn('billing', response.data)
        self.assertIn('internal_notes', response.data)

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
        version = SupplierDocumentVersion.objects.get(document=self.document, revision='A')
        self.assertEqual(version.approved_by, self.manager.email)
        self.assertIsNotNone(version.approved_at)

    def test_document_obsolete_requires_reason_and_sets_obsolete_date(self):
        missing_reason = self.auth_client.post(
            f"{reverse('medsupplier-document-detail', args=[self.document.id])}obsolete/?organization_id={self.org_a.id}",
            {},
            format='json',
        )
        self.assertEqual(missing_reason.status_code, 400)

        response = self.auth_client.post(
            f"{reverse('medsupplier-document-detail', args=[self.document.id])}obsolete/?organization_id={self.org_a.id}",
            {'reason': 'Controlled document superseded by new revision.'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.document.refresh_from_db()
        self.assertEqual(self.document.status, 'obsolete')
        self.assertEqual(self.document.obsolete_date, date.today())

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

    def test_quote_revise_clones_private_supplier_view_and_lines(self):
        self.quote.internal_notes = 'Supplier-only quote context.'
        self.quote.valid_until = date.today() + timedelta(days=15)
        self.quote.save(update_fields=['internal_notes', 'valid_until'])
        response = self.auth_client.post(
            f"{reverse('medsupplier-quote-detail', args=[self.quote.id])}revise/?organization_id={self.org_a.id}",
            {'reason': 'Customer requested corrected item revision.'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        revised = SupplierQuote.objects.get(id=response.data['id'])
        self.assertEqual(revised.status, 'draft')
        self.assertEqual(revised.metadata['previous_quote_id'], self.quote.id)
        self.assertEqual(revised.metadata['revision'], 2)
        self.assertEqual(revised.lines.count(), 1)
        self.assertEqual(revised.internal_notes, 'Supplier-only quote context.')
        self.assertTrue(
            MedSupplierAuditEvent.objects.filter(
                record_type='supplierquote',
                record_id=str(self.quote.id),
                reason='Customer requested corrected item revision.',
            ).exists()
        )

    def test_purchase_order_traceability_returns_lines_lots_shipments_and_inspections(self):
        SupplierOrderLine.objects.create(
            organization=self.org_a,
            account=self.account_a,
            purchase_order=self.purchase_order,
            line_number=1,
            product_code='POUCH-001',
            description='Sterile pouch',
            quantity='100.000',
            pending_quantity='50.000',
            visibility='customer_shared',
        )
        SupplierLot.objects.create(
            organization=self.org_a,
            account=self.account_a,
            purchase_order=self.purchase_order,
            lot_number='LOT-TRACE-001',
            product_code='POUCH-001',
            quantity='100.000',
            visibility='customer_shared',
        )
        shipment = SupplierShipment.objects.create(
            organization=self.org_a,
            account=self.account_a,
            purchase_order=self.purchase_order,
            shipment_number='SHIP-TRACE-001',
            status='in_transit',
            asn_number='ASN-001',
            pod_reference='POD-PENDING',
            expected_delivery_date=date.today() + timedelta(days=3),
            visibility='customer_shared',
        )
        SupplierShipmentMilestone.objects.create(
            organization=self.org_a,
            account=self.account_a,
            shipment=shipment,
            milestone_type='ASN',
            status='completed',
            visibility='customer_shared',
        )
        SupplierInspection.objects.create(
            organization=self.org_a,
            account=self.account_a,
            shipment=shipment,
            inspection_number='INSP-TRACE-001',
            result='pending',
            visibility='customer_shared',
        )
        response = self.auth_client.get(
            f"{reverse('medsupplier-purchase-order-detail', args=[self.purchase_order.id])}traceability/?organization_id={self.org_a.id}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['purchase_order']['po_number'], 'PO-MED-A-001')
        self.assertEqual(response.data['lines'][0]['product_code'], 'POUCH-001')
        self.assertEqual(response.data['lots'][0]['lot_number'], 'LOT-TRACE-001')
        self.assertEqual(response.data['shipments'][0]['asn_number'], 'ASN-001')
        self.assertEqual(response.data['inspections'][0]['inspection_number'], 'INSP-TRACE-001')

    def test_capa_add_action_records_action_metadata_and_audit_trail(self):
        response = self.auth_client.post(
            f"{reverse('medsupplier-capa-detail', args=[self.capa.id])}add-action/?organization_id={self.org_a.id}",
            {
                'action': 'Verify label revision lock in ERP.',
                'owner': 'Quality Lead',
                'due_date': str(date.today() + timedelta(days=7)),
                'reason': 'CAPA action plan updated.',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.capa.refresh_from_db()
        self.assertEqual(self.capa.metadata['actions'][0]['action'], 'Verify label revision lock in ERP.')
        self.assertTrue(
            MedSupplierAuditEvent.objects.filter(
                record_type='suppliercapa',
                record_id=str(self.capa.id),
                action='update',
                reason='CAPA action plan updated.',
            ).exists()
        )

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

    def test_evidence_package_index_and_html_export_are_available(self):
        package = EvidencePackage.objects.create(
            organization=self.org_a,
            account=self.account_a,
            package_number='EP-HTML-001',
            title='Traceability evidence',
            status='prepared',
            checksum='abc123',
            visibility='regulated_evidence',
        )
        EvidencePackageEntry.objects.create(
            package=package,
            object_type='supplierpurchaseorder',
            object_id=str(self.purchase_order.id),
            label='Purchase order traceability',
        )
        index_response = self.auth_client.get(
            f"{reverse('medsupplier-evidence-package-detail', args=[package.id])}index/?organization_id={self.org_a.id}",
        )
        self.assertEqual(index_response.status_code, 200)
        self.assertEqual(index_response.data['entry_count'], 1)
        self.assertIn('supplierpurchaseorder', index_response.data['objects'])

        html_response = self.auth_client.get(
            f"{reverse('medsupplier-evidence-package-detail', args=[package.id])}export/?organization_id={self.org_a.id}&file_format=html",
        )
        self.assertEqual(html_response.status_code, 200)
        self.assertEqual(html_response['Content-Type'], 'text/html')
        self.assertIn(b'Purchase order traceability', html_response.content)

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
        mocked_adminapps.validate_product_access.return_value = {
            'allowed': True,
            'reason': 'ok',
            'source': 'adminapps',
            'product': {
                'code': 'MEDSUPPLIER',
                'enabled': True,
                'access_allowed': True,
                'billing_status': 'active',
            },
            'source': 'adminapps',
        }

        response = self.auth_client.get(self.integration_status_url, {'organization_id': self.org_a.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['module_code'], 'MEDSUPPLIER')
        self.assertTrue(response.data['adminapps_authority']['organizations'])
        self.assertTrue(response.data['adminapps_authority']['users'])
        self.assertTrue(response.data['adminapps_authority']['product_access'])
        self.assertTrue(response.data['entitlement']['enabled'])
        self.assertEqual(response.data['entitlement']['reason'], 'ok')


class MedSupplierAdminAppsClientTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(
            name='MedSupplier Client Org',
            slug='medsupplier-client-org',
            email='client@example.com',
            is_active=True,
        )
        self.user = get_user_model().objects.create_user(
            username='client_scope_user',
            email='client-scope@example.com',
            password='StrongPass@123',
        )
        self.account = SupplierAccount.objects.create(
            organization=self.org,
            name='Scoped Account',
            account_code='SCOPED-001',
            status='active',
        )

    @override_settings(
        IS_PRODUCTION=False,
        ADMIN_APPS_INTEGRATION={
            'BASE_URL': 'http://adminapps.test/api/integration',
            'API_KEY': 'test-key',
            'TIMEOUT': 1,
            'CACHE_TTL': 0,
            'ALLOW_LOCAL_FALLBACK': True,
        },
    )
    def test_product_access_uses_explicit_local_fallback_only_with_scope(self):
        MedSupplierUserScope.objects.create(
            user=self.user,
            organization=self.org,
            account=self.account,
            side='supplier',
            role='supplier_admin',
        )
        client = AdminAppsClient()

        with patch.object(client, '_make_request', return_value={'error': 'Timeout', 'code': 'timeout'}):
            result = client.validate_product_access(self.org.id, 'MEDSUPPLIER', use_cache=False)

        self.assertTrue(result['allowed'])
        self.assertTrue(result['fallback'])
        self.assertEqual(result['source'], 'local_database')
        self.assertEqual(result['reason'], 'ok')

    @override_settings(
        IS_PRODUCTION=False,
        ADMIN_APPS_INTEGRATION={
            'BASE_URL': 'http://adminapps.test/api/integration',
            'API_KEY': 'test-key',
            'TIMEOUT': 1,
            'CACHE_TTL': 0,
            'ALLOW_LOCAL_FALLBACK': True,
        },
    )
    def test_product_access_does_not_bypass_adminapps_business_denial(self):
        client = AdminAppsClient()

        with patch.object(
            client,
            '_make_request',
            return_value={
                'allowed': False,
                'reason': 'billing_blocked',
                'product': {'code': 'MEDSUPPLIER', 'billing_status': 'past_due'},
            },
        ):
            result = client.validate_product_access(self.org.id, 'MEDSUPPLIER', use_cache=False)

        self.assertFalse(result['allowed'])
        self.assertEqual(result['source'], 'adminapps')
        self.assertEqual(result['reason'], 'billing_blocked')
        self.assertNotIn('fallback', result)

    @override_settings(
        IS_PRODUCTION=True,
        ADMIN_APPS_INTEGRATION={
            'BASE_URL': 'http://adminapps.test/api/integration',
            'API_KEY': 'test-key',
            'TIMEOUT': 1,
            'CACHE_TTL': 0,
            'ALLOW_LOCAL_FALLBACK': True,
        },
    )
    def test_product_access_fails_closed_in_production_when_adminapps_unavailable(self):
        client = AdminAppsClient()

        with patch.object(client, '_make_request', return_value={'error': 'Timeout', 'code': 'timeout'}):
            result = client.validate_product_access(self.org.id, 'MEDSUPPLIER', use_cache=False)

        self.assertFalse(result['allowed'])
        self.assertEqual(result['source'], 'fail_closed')
        self.assertEqual(result['reason'], 'timeout')

    @override_settings(
        IS_PRODUCTION=False,
        ADMIN_APPS_INTEGRATION={
            'BASE_URL': 'http://adminapps.test/api/integration',
            'API_KEY': 'test-key',
            'TIMEOUT': 1,
            'CACHE_TTL': 0,
            'ALLOW_LOCAL_FALLBACK': True,
        },
    )
    def test_adminapps_smoke_no_fallback_passes_with_direct_adminapps_access(self):
        MedSupplierUserScope.objects.create(
            user=self.user,
            organization=self.org,
            account=self.account,
            side='supplier',
            role='supplier_admin',
        )
        out = StringIO()

        with patch(
            'medsupplier.management.commands.check_medsupplier_adminapps.admin_apps_client.health_check',
            return_value={'status': 'ok'},
        ), patch(
            'medsupplier.management.commands.check_medsupplier_adminapps.admin_apps_client.validate_product_access',
            return_value={'allowed': True, 'reason': 'ok', 'source': 'adminapps'},
        ):
            call_command(
                'check_medsupplier_adminapps',
                organization_slug=self.org.slug,
                no_fallback=True,
                stdout=out,
            )

        self.assertIn('fallback_allowed=False', out.getvalue())
        self.assertIn('product_access_source=adminapps', out.getvalue())

    @override_settings(
        IS_PRODUCTION=False,
        ADMIN_APPS_INTEGRATION={
            'BASE_URL': 'http://adminapps.test/api/integration',
            'API_KEY': 'test-key',
            'TIMEOUT': 1,
            'CACHE_TTL': 0,
            'ALLOW_LOCAL_FALLBACK': True,
        },
    )
    def test_adminapps_smoke_no_fallback_rejects_local_fallback(self):
        MedSupplierUserScope.objects.create(
            user=self.user,
            organization=self.org,
            account=self.account,
            side='supplier',
            role='supplier_admin',
        )

        with patch(
            'medsupplier.management.commands.check_medsupplier_adminapps.admin_apps_client.health_check',
            return_value={'status': 'ok'},
        ), patch(
            'medsupplier.management.commands.check_medsupplier_adminapps.admin_apps_client.validate_product_access',
            return_value={'allowed': True, 'reason': 'ok', 'source': 'local_database', 'fallback': True},
        ), self.assertRaisesMessage(CommandError, 'fallback was used'):
            call_command(
                'check_medsupplier_adminapps',
                organization_slug=self.org.slug,
                no_fallback=True,
            )


class MedSupplierEndpointRoleMatrixTests(TestCase):
    """Executable endpoint/role matrix for the Stage 6 security gate."""

    SUPPLIER_ROLES = [
        'supplier_admin',
        'supplier_sales',
        'supplier_finance',
        'supplier_quality',
        'supplier_logistics',
        'supplier_viewer',
    ]
    CUSTOMER_ROLES = [
        'customer_admin',
        'customer_buyer',
        'customer_quality',
        'customer_logistics',
        'customer_auditor',
        'customer_viewer',
    ]
    PRIVATE_FIELDS = {
        'private_margin_notes',
        'supplier_cost',
        'margin',
        'commission',
        'advance',
        'internal_notes',
        'pricing_internal',
        'forecast_probability',
    }

    def setUp(self):
        self.org = Organization.objects.create(name='Matrix Org', slug='matrix-org', email='matrix@example.com')
        self.other_org = Organization.objects.create(name='Matrix Other Org', slug='matrix-other-org', email='matrix-other@example.com')

        self.account = SupplierAccount.objects.create(
            organization=self.org,
            name='Matrix Shared Account',
            account_code='MX-SHARED',
            status='active',
            visibility='customer_shared',
        )
        self.private_account = SupplierAccount.objects.create(
            organization=self.org,
            name='Matrix Private Account',
            account_code='MX-PRIVATE',
            status='active',
            visibility='supplier_private',
        )
        self.unscoped_account = SupplierAccount.objects.create(
            organization=self.org,
            name='Matrix Unscoped Account',
            account_code='MX-UNSCOPED',
            status='active',
            visibility='customer_shared',
        )
        self.other_account = SupplierAccount.objects.create(
            organization=self.other_org,
            name='Matrix Other Tenant Account',
            account_code='MX-OTHER',
            status='active',
            visibility='customer_shared',
        )

        self.document = SupplierDocument.objects.create(
            organization=self.org,
            account=self.account,
            document_number='MX-DOC-001',
            title='Matrix Document',
            document_type='COC',
            status='draft',
            visibility='customer_shared',
        )
        self.rfq = SupplierRFQ.objects.create(
            organization=self.org,
            account=self.account,
            rfq_number='MX-RFQ-001',
            title='Matrix RFQ',
            status='sent',
            visibility='customer_shared',
        )
        self.quote = SupplierQuote.objects.create(
            organization=self.org,
            account=self.account,
            rfq=self.rfq,
            quote_number='MX-Q-001',
            status='submitted',
            visibility='customer_shared',
            total_amount='1000.00',
            supplier_cost='600.00',
            margin='40.00',
            commission='25.00',
            advance='100.00',
            private_margin_notes='private margin',
            internal_notes='internal note',
            forecast_probability=80,
        )
        self.purchase_order = SupplierPurchaseOrder.objects.create(
            organization=self.org,
            account=self.account,
            quote=self.quote,
            po_number='MX-PO-001',
            status='in_production',
            visibility='customer_shared',
        )
        self.shipment = SupplierShipment.objects.create(
            organization=self.org,
            account=self.account,
            purchase_order=self.purchase_order,
            shipment_number='MX-SHIP-001',
            status='in_transit',
            visibility='customer_shared',
        )
        self.quality_event = SupplierQualityEvent.objects.create(
            organization=self.org,
            account=self.account,
            event_number='MX-NCR-001',
            event_type='ncr',
            severity='medium',
            status='closed',
            title='Matrix NCR',
            description='Closed quality event for matrix.',
            visibility='customer_shared',
        )
        self.capa = SupplierCAPA.objects.create(
            organization=self.org,
            account=self.account,
            quality_event=self.quality_event,
            capa_number='MX-CAPA-001',
            status='closed',
            root_cause='Root cause',
            corrective_action='Corrective action',
            effectiveness_result='Effective',
            evidence_summary='Evidence',
            visibility='customer_shared',
        )
        self.fmea = SupplierFMEA.objects.create(
            organization=self.org,
            account=self.account,
            fmea_number='MX-FMEA-001',
            title='Matrix FMEA',
            status='active',
            visibility='customer_shared',
        )
        self.evidence_package = EvidencePackage.objects.create(
            organization=self.org,
            account=self.account,
            package_number='MX-EP-001',
            title='Matrix Evidence Package',
            status='prepared',
            visibility='regulated_evidence',
        )
        EvidencePackageEntry.objects.create(
            package=self.evidence_package,
            object_type='medsupplier.supplierdocument',
            object_id=str(self.document.id),
            label='Matrix document',
        )
        MedSupplierAuditEvent.objects.create(
            organization=self.org,
            account=self.account,
            action='create',
            record_type='supplierdocument',
            record_id=str(self.document.id),
            object_type='medsupplier.supplierdocument',
            object_id=str(self.document.id),
            description='Matrix exportable audit event',
            exportable=True,
        )
        MedSupplierAuditEvent.objects.create(
            organization=self.org,
            account=self.private_account,
            action='create',
            record_type='supplieraccount',
            record_id=str(self.private_account.id),
            description='Matrix private audit event',
            exportable=False,
        )

        self.clients = {}
        user_model = get_user_model()
        for role in self.SUPPLIER_ROLES + self.CUSTOMER_ROLES:
            user = user_model.objects.create_user(
                username=f'matrix_{role}',
                email=f'matrix_{role}@example.com',
                password='StrongPass@123',
            )
            account = None if role.startswith('supplier_') else self.account
            MedSupplierUserScope.objects.create(
                user=user,
                organization=self.org,
                account=account,
                side='supplier' if role.startswith('supplier_') else 'customer',
                role=role,
            )
            client = APIClient()
            client.force_authenticate(user=user)
            self.clients[role] = client

    def _url(self, path, org=None):
        return f'/api/medsupplier/{path}?organization_id={org or self.org.id}'

    def _results(self, response):
        payload = response.json()
        return payload.get('results', payload if isinstance(payload, list) else [])

    def _first_result(self, response):
        results = self._results(response)
        self.assertTrue(results, response.content)
        return results[0]

    def test_supplier_admin_can_read_minimum_endpoint_matrix(self):
        client = self.clients['supplier_admin']
        with patch('medsupplier.views.admin_apps_client') as mocked_adminapps:
            mocked_adminapps.health_check.return_value = {'status': 'ok'}
            mocked_adminapps.validate_product_access.return_value = {
                'allowed': True,
                'reason': 'ok',
                'source': 'adminapps',
                'product': {'code': 'MEDSUPPLIER', 'access_allowed': True},
            }
            endpoints = [
                'accounts/',
                'dashboard/summary/',
                'me/permissions/',
                'quotes/',
                'purchase-orders/',
                'shipments/',
                'documents/',
                'capas/',
                'fmeas/',
                'evidence-packages/',
                'audit-events/',
                'integration/status/',
            ]
            for endpoint in endpoints:
                response = client.get(self._url(endpoint))
                self.assertEqual(response.status_code, 200, endpoint)

    def test_customer_roles_are_scoped_and_do_not_see_private_or_unscoped_accounts(self):
        for role in self.CUSTOMER_ROLES:
            response = self.clients[role].get(self._url('accounts/'))
            self.assertEqual(response.status_code, 200, role)
            account_codes = {item['account_code'] for item in self._results(response)}
            self.assertIn('MX-SHARED', account_codes)
            self.assertNotIn('MX-PRIVATE', account_codes)
            self.assertNotIn('MX-UNSCOPED', account_codes)

    def test_customer_roles_do_not_receive_private_financial_quote_fields(self):
        for role in self.CUSTOMER_ROLES:
            response = self.clients[role].get(self._url('quotes/'))
            self.assertEqual(response.status_code, 200, role)
            quote = self._first_result(response)
            self.assertTrue(self.PRIVATE_FIELDS.isdisjoint(quote.keys()), role)

    def test_supplier_quality_and_logistics_do_not_receive_private_financial_quote_fields(self):
        for role in ['supplier_quality', 'supplier_logistics']:
            response = self.clients[role].get(self._url('quotes/'))
            self.assertEqual(response.status_code, 200, role)
            quote = self._first_result(response)
            self.assertTrue(self.PRIVATE_FIELDS.isdisjoint(quote.keys()), role)

    def test_supplier_finance_can_receive_private_financial_quote_fields(self):
        response = self.clients['supplier_finance'].get(self._url('quotes/'))
        self.assertEqual(response.status_code, 200)
        quote = self._first_result(response)
        for field in ['supplier_cost', 'margin', 'commission', 'advance', 'internal_notes']:
            self.assertIn(field, quote)

    def test_private_cockpit_access_is_limited_to_authorized_supplier_roles(self):
        for role in ['supplier_admin', 'supplier_sales', 'supplier_finance']:
            response = self.clients[role].get(self._url('cockpit/private/'))
            self.assertEqual(response.status_code, 200, role)
            self.assertIn('finance', response.json())

        for role in ['supplier_quality', 'supplier_logistics', 'supplier_viewer'] + self.CUSTOMER_ROLES:
            response = self.clients[role].get(self._url('cockpit/private/'))
            self.assertEqual(response.status_code, 403, role)

    def test_read_only_and_customer_roles_cannot_mutate_accounts(self):
        blocked_roles = ['supplier_viewer'] + self.CUSTOMER_ROLES
        for role in blocked_roles:
            response = self.clients[role].post(
                self._url('accounts/'),
                {
                    'name': f'Blocked {role}',
                    'account_code': f'BLOCK-{role}',
                    'status': 'prospect',
                },
                format='json',
            )
            self.assertEqual(response.status_code, 403, role)

    def test_supplier_admin_can_mutate_and_audit_event_is_created(self):
        response = self.clients['supplier_admin'].post(
            self._url('accounts/'),
            {
                'name': 'Matrix Created Account',
                'account_code': 'MX-CREATED',
                'status': 'prospect',
                'visibility': 'supplier_private',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            MedSupplierAuditEvent.objects.filter(
                organization=self.org,
                action='create',
                record_type='supplieraccount',
                record_id=str(response.json()['id']),
            ).exists()
        )

    def test_cross_tenant_access_is_blocked(self):
        response = self.clients['supplier_admin'].get(self._url('accounts/', org=self.other_org.id))
        self.assertEqual(response.status_code, 403)

    def test_customer_detail_outside_account_scope_is_hidden(self):
        response = self.clients['customer_buyer'].get(self._url(f'accounts/{self.unscoped_account.id}/'))
        self.assertEqual(response.status_code, 404)

    def test_customer_audit_trail_is_read_only_and_redacted(self):
        response = self.clients['customer_auditor'].get(self._url('audit-events/'))
        self.assertEqual(response.status_code, 200)
        event = self._first_result(response)
        self.assertNotIn('old_values', event)
        self.assertNotIn('new_values', event)
        self.assertNotIn('ip_address', event)

        export_response = self.clients['customer_auditor'].get(self._url('audit-events/export/'))
        self.assertEqual(export_response.status_code, 200)

        mutation = self.clients['customer_auditor'].post(
            self._url('accounts/'),
            {
                'name': 'Blocked Auditor Account',
                'account_code': 'AUD-BLOCK',
                'status': 'prospect',
            },
            format='json',
        )
        self.assertEqual(mutation.status_code, 403)
