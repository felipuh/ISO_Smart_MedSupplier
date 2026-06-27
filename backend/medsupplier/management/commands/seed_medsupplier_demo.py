from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from authentication.models import UserProfile
from core.models import Organization
from medsupplier import models


class Command(BaseCommand):
    help = 'Seed demo data for ISO Smart MedSupplier functional QA and sales demos.'

    def add_arguments(self, parser):
        parser.add_argument('--organization-slug', default='medsupplier-demo')
        parser.add_argument('--organization-name', default='MedSupplier Demo Workspace')
        parser.add_argument('--user-email', default='medsupplier.demo@smart3ai.local')
        parser.add_argument('--user-password', default='MedSupplierDemo@123')

    def handle(self, *args, **options):
        org, _ = Organization.objects.get_or_create(
            slug=options['organization_slug'],
            defaults={
                'name': options['organization_name'],
                'email': 'medsupplier-demo@smart3ai.local',
            },
        )
        user_model = get_user_model()
        user, user_created = user_model.objects.get_or_create(
            email=options['user_email'],
            defaults={
                'username': options['user_email'].split('@')[0],
                'first_name': 'MedSupplier',
                'last_name': 'Demo',
                'is_active': True,
            },
        )
        if user_created:
            user.set_password(options['user_password'])
            user.save(update_fields=['password'])
        UserProfile.objects.update_or_create(
            user=user,
            organization=org,
            defaults={
                'role': 'iso_manager',
                'job_title': 'Supplier Quality Lead',
                'department': 'Quality',
                'is_active': True,
            },
        )

        today = timezone.now().date()

        account, _ = models.SupplierAccount.objects.update_or_create(
            organization=org,
            account_code='MS-DEMO-001',
            defaults={
                'name': 'CardioNova Medical Devices',
                'legal_name': 'CardioNova Medical Devices Inc.',
                'regulated_industry': True,
                'customer_segment': 'Medical Devices Tier 1',
                'country': 'United States',
                'primary_contact_email': 'quality@cardionova.example',
                'account_owner': 'Supplier Quality Lead',
                'status': 'active',
                'risk_level': 'high',
                'next_qbr_date': today.replace(day=28),
                'visibility': 'shared',
            },
        )

        private_account, _ = models.SupplierAccount.objects.update_or_create(
            organization=org,
            account_code='MS-DEMO-PRIVATE',
            defaults={
                'name': 'Strategic Private Pipeline',
                'regulated_industry': True,
                'customer_segment': 'Confidential opportunity',
                'country': 'Costa Rica',
                'account_owner': 'Commercial Director',
                'status': 'prospect',
                'risk_level': 'medium',
                'visibility': 'private',
            },
        )

        contact, _ = models.SupplierContact.objects.update_or_create(
            organization=org,
            account=account,
            email='maria.chen@cardionova.example',
            defaults={
                'full_name': 'Maria Chen',
                'role_title': 'Supplier Quality Manager',
                'department': 'Quality',
                'phone': '+1 555 0100',
                'is_customer_user': True,
                'is_active': True,
                'visibility': 'shared',
            },
        )

        meeting, _ = models.SupplierMeeting.objects.update_or_create(
            organization=org,
            account=account,
            title='QBR Supplier-Customer Readiness Review',
            defaults={
                'status': 'completed',
                'agenda': 'Open actions, shipment reliability, NCR trend and CAPA effectiveness.',
                'minutes': 'Customer requested tighter evidence package before next shipment release.',
                'attendees': [contact.email],
                'decisions': ['CAPA effectiveness evidence due before next QBR.'],
                'visibility': 'shared',
            },
        )

        models.SupplierAction.objects.update_or_create(
            organization=org,
            account=account,
            title='Enviar paquete de evidencia CAPA al cliente',
            defaults={
                'meeting': meeting,
                'owner': 'Supplier Quality Lead',
                'due_date': today,
                'status': 'in_progress',
                'description': 'Compilar investigacion, causa raiz, acciones y verificacion de efectividad.',
                'visibility': 'shared',
            },
        )

        requirement, _ = models.SupplierRequirement.objects.update_or_create(
            organization=org,
            requirement_id='CN-REQ-001',
            defaults={
                'account': account,
                'title': 'Evidence package required before product release',
                'requirement_type': 'customer',
                'source_reference': 'CardioNova Supplier Quality Agreement',
                'description': 'Each release must include inspection record, COC and open NCR status.',
                'status': 'approved',
                'effective_date': today,
                'owner': 'Quality Systems',
                'visibility': 'shared',
            },
        )

        document, _ = models.SupplierDocument.objects.update_or_create(
            organization=org,
            document_number='MS-DOC-COC-001',
            defaults={
                'account': account,
                'title': 'Certificate of Conformance Template',
                'document_type': 'COC',
                'current_revision': 'B',
                'status': 'effective',
                'confidentiality': 'controlled',
                'owner': 'Document Control',
                'effective_date': today,
                'visibility': 'shared',
            },
        )

        models.SupplierDocumentVersion.objects.update_or_create(
            organization=org,
            document=document,
            revision='B',
            defaults={
                'change_reason': 'Added lot traceability field required by customer.',
                'checksum': 'demo-checksum-coc-b',
                'approved_by': 'Quality Director',
                'approved_at': timezone.now(),
                'visibility': 'shared',
            },
        )

        rfq, _ = models.SupplierRFQ.objects.update_or_create(
            organization=org,
            rfq_number='RFQ-CN-2026-001',
            defaults={
                'account': account,
                'title': 'Sterile pouch packaging pilot run',
                'status': 'quoted',
                'requested_due_date': today,
                'notes': 'Customer requested expedited validation evidence.',
                'visibility': 'shared',
            },
        )
        rfq.requirements.set([requirement])

        quote, _ = models.SupplierQuote.objects.update_or_create(
            organization=org,
            quote_number='Q-CN-2026-001',
            defaults={
                'account': account,
                'rfq': rfq,
                'status': 'approved',
                'currency': 'USD',
                'total_amount': Decimal('48500.00'),
                'valid_until': today,
                'private_margin_notes': 'Margin review approved internally.',
                'visibility': 'private',
            },
        )

        po, _ = models.SupplierPurchaseOrder.objects.update_or_create(
            organization=org,
            po_number='PO-CN-10045',
            defaults={
                'account': account,
                'quote': quote,
                'status': 'in_production',
                'customer_po_date': today,
                'promised_ship_date': today,
                'currency': 'USD',
                'total_amount': Decimal('48500.00'),
                'visibility': 'shared',
            },
        )

        lot, _ = models.SupplierLot.objects.update_or_create(
            organization=org,
            lot_number='LOT-CN-26-0001',
            defaults={
                'account': account,
                'purchase_order': po,
                'product_code': 'STER-POUCH-XL',
                'product_description': 'Sterile barrier pouch, XL',
                'quantity': Decimal('12000.000'),
                'uom': 'EA',
                'manufactured_at': today,
                'expiration_at': today.replace(year=today.year + 2),
                'visibility': 'shared',
            },
        )

        shipment, _ = models.SupplierShipment.objects.update_or_create(
            organization=org,
            shipment_number='SHP-CN-0001',
            defaults={
                'account': account,
                'purchase_order': po,
                'status': 'in_transit',
                'carrier': 'DHL',
                'tracking_number': 'DEMO-TRACK-0001',
                'shipped_at': timezone.now(),
                'visibility': 'shared',
            },
        )

        inspection, _ = models.SupplierInspection.objects.update_or_create(
            organization=org,
            inspection_number='INSP-CN-0001',
            defaults={
                'account': account,
                'shipment': shipment,
                'received_at': timezone.now(),
                'result': 'accepted_with_deviation',
                'inspected_by': 'Incoming Quality',
                'findings': f'Lot {lot.lot_number} accepted with labeling deviation.',
                'visibility': 'shared',
            },
        )

        quality_event, _ = models.SupplierQualityEvent.objects.update_or_create(
            organization=org,
            event_number='NCR-CN-0001',
            defaults={
                'account': account,
                'inspection': inspection,
                'event_type': 'ncr',
                'severity': 'medium',
                'status': 'capa_required',
                'title': 'Label traceability mismatch',
                'description': 'Mismatch between pouch label revision and COC evidence package.',
                'owner': 'Supplier Quality Lead',
                'visibility': 'shared',
            },
        )

        models.SupplierCAPA.objects.update_or_create(
            organization=org,
            capa_number='CAPA-CN-0001',
            defaults={
                'account': account,
                'quality_event': quality_event,
                'status': 'effectiveness_check',
                'root_cause': 'Document control handoff missed label revision validation.',
                'corrective_action': 'Updated release checklist and added independent document review.',
                'preventive_action': 'Automated reminder before shipment release.',
                'owner': 'Quality Systems',
                'due_date': today,
                'effectiveness_result': 'Pending final shipment verification.',
                'visibility': 'shared',
            },
        )

        models.SupplierScorecard.objects.update_or_create(
            organization=org,
            account=account,
            period_start=today.replace(day=1),
            period_end=today,
            defaults={
                'quality_score': Decimal('88.00'),
                'delivery_score': Decimal('92.00'),
                'responsiveness_score': Decimal('95.00'),
                'overall_score': Decimal('91.67'),
                'qbr_notes': 'Strong responsiveness; quality trend needs CAPA closure evidence.',
                'visibility': 'shared',
            },
        )

        self.stdout.write(self.style.SUCCESS(
            f'MedSupplier demo seeded for organization {org.name} ({org.slug}). '
            f'Accounts: {account.account_code}, {private_account.account_code}. '
            f'User: {user.email}'
        ))
