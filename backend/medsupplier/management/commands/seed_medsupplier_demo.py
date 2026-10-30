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
                'visibility': 'customer_shared',
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
                'visibility': 'supplier_private',
            },
        )

        user_model = get_user_model()

        def ensure_demo_user(email, role, side, account_scope=None, first_name='MedSupplier', last_name='Demo'):
            user, _ = user_model.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                },
            )
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
            if hasattr(user, 'must_change_password'):
                user.must_change_password = False
            if hasattr(user, 'temporary_password_set_at'):
                user.temporary_password_set_at = None
            if hasattr(user, 'failed_login_attempts'):
                user.failed_login_attempts = 0
            if hasattr(user, 'account_locked_until'):
                user.account_locked_until = None
            update_fields = ['first_name', 'last_name', 'is_active']
            if not user.check_password(options['user_password']):
                user.set_password(options['user_password'])
                update_fields.append('password')
            for field_name in ['must_change_password', 'temporary_password_set_at', 'failed_login_attempts', 'account_locked_until']:
                if hasattr(user, field_name):
                    update_fields.append(field_name)
            user.save(update_fields=update_fields)

            profile_role = 'iso_manager' if side == 'supplier' else 'auditor'
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'organization': org,
                    'role': profile_role,
                    'job_title': role.replace('_', ' ').title(),
                    'department': 'MedSupplier Demo',
                    'is_active': True,
                },
            )
            models.MedSupplierUserScope.objects.update_or_create(
                user=user,
                organization=org,
                account=account_scope,
                role=role,
                defaults={
                    'side': side,
                    'is_active': True,
                },
            )
            return user

        user = ensure_demo_user(
            options['user_email'],
            'supplier_finance',
            'supplier',
            first_name='MedSupplier',
            last_name='Finance Demo',
        )
        role_users = {
            'supplier_admin': ensure_demo_user('medsupplier.supplier.admin@smart3ai.local', 'supplier_admin', 'supplier'),
            'supplier_finance': user,
            'supplier_quality': ensure_demo_user('medsupplier.supplier.quality@smart3ai.local', 'supplier_quality', 'supplier'),
            'supplier_logistics': ensure_demo_user('medsupplier.supplier.logistics@smart3ai.local', 'supplier_logistics', 'supplier'),
            'supplier_viewer': ensure_demo_user('medsupplier.supplier.viewer@smart3ai.local', 'supplier_viewer', 'supplier'),
            'customer_admin': ensure_demo_user('medsupplier.customer.admin@smart3ai.local', 'customer_admin', 'customer', account),
            'customer_buyer': ensure_demo_user('medsupplier.customer.buyer@smart3ai.local', 'customer_buyer', 'customer', account),
            'customer_quality': ensure_demo_user('medsupplier.customer.quality@smart3ai.local', 'customer_quality', 'customer', account),
            'customer_auditor': ensure_demo_user('medsupplier.customer.auditor@smart3ai.local', 'customer_auditor', 'customer', account),
            'customer_viewer': ensure_demo_user('medsupplier.customer.viewer@smart3ai.local', 'customer_viewer', 'customer', account),
        }

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
                'visibility': 'customer_shared',
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
                'visibility': 'customer_shared',
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
                'visibility': 'customer_shared',
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
                'visibility': 'regulated_evidence',
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
                'visibility': 'regulated_evidence',
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
                'visibility': 'customer_shared',
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
                'supplier_cost': Decimal('30500.00'),
                'margin': Decimal('37.11'),
                'commission': Decimal('1200.00'),
                'advance': Decimal('5000.00'),
                'forecast_probability': 85,
                'internal_notes': 'Private supplier-side forecast and commercial terms.',
                'visibility': 'customer_shared',
            },
        )
        quote_line, _ = models.SupplierQuoteLine.objects.update_or_create(
            organization=org,
            quote=quote,
            line_number=1,
            defaults={
                'account': account,
                'rfq': rfq,
                'product_code': 'STER-POUCH-XL',
                'description': 'Sterile barrier pouch, XL',
                'technical_description': 'Medical device sterile barrier packaging pilot line.',
                'quantity': Decimal('12000.000'),
                'uom': 'EA',
                'moq': Decimal('10000.000'),
                'lead_time_days': 28,
                'incoterm': 'DAP',
                'unit_price': Decimal('4.0417'),
                'supplier_cost': Decimal('2.5417'),
                'margin': Decimal('37.11'),
                'currency': 'USD',
                'customer_notes': 'Includes controlled release evidence package.',
                'internal_notes': 'Cost basis approved by finance.',
                'visibility': 'customer_shared',
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
                'visibility': 'customer_shared',
            },
        )
        models.SupplierOrderLine.objects.update_or_create(
            organization=org,
            purchase_order=po,
            line_number=1,
            defaults={
                'account': account,
                'quote_line': quote_line,
                'product_code': 'STER-POUCH-XL',
                'description': 'Sterile barrier pouch, XL',
                'quantity': Decimal('12000.000'),
                'delivered_quantity': Decimal('0.000'),
                'pending_quantity': Decimal('12000.000'),
                'uom': 'EA',
                'due_date': today,
                'status': 'confirmed',
                'visibility': 'customer_shared',
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
                'visibility': 'customer_shared',
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
                'visibility': 'customer_shared',
            },
        )
        models.SupplierShipmentMilestone.objects.update_or_create(
            organization=org,
            shipment=shipment,
            milestone_type='ASN issued',
            defaults={
                'account': account,
                'status': 'completed',
                'expected_at': timezone.now(),
                'actual_at': timezone.now(),
                'carrier': 'DHL',
                'tracking_number': shipment.tracking_number,
                'visibility': 'customer_shared',
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
                'visibility': 'customer_shared',
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
                'visibility': 'customer_shared',
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
                'evidence_summary': 'Release checklist, document review, and shipment verification evidence available.',
                'visibility': 'customer_shared',
            },
        )
        fmea, _ = models.SupplierFMEA.objects.update_or_create(
            organization=org,
            fmea_number='FMEA-CN-STER-001',
            defaults={
                'account': account,
                'title': 'Sterile pouch packaging process FMEA',
                'process': 'Packaging and release',
                'status': 'active',
                'owner': 'Supplier Quality Lead',
                'review_due_date': today,
                'visibility': 'customer_shared',
            },
        )
        models.SupplierFMEAItem.objects.update_or_create(
            organization=org,
            fmea=fmea,
            failure_mode='Label revision mismatch',
            defaults={
                'account': account,
                'quality_event': quality_event,
                'hazard': 'Incorrect released documentation',
                'cause': 'Manual handoff missed document revision check.',
                'effect': 'COC evidence mismatch at customer receiving.',
                'severity': 4,
                'occurrence': 3,
                'detection': 2,
                'mitigation': 'Independent release checklist verification.',
                'owner': 'Quality Systems',
                'status': 'mitigating',
                'visibility': 'customer_shared',
            },
        )
        evidence_package, _ = models.EvidencePackage.objects.update_or_create(
            organization=org,
            package_number='EP-CN-0001',
            defaults={
                'account': account,
                'title': 'CAPA and release evidence package',
                'scope': 'CAPA / shipment release',
                'date_from': today.replace(day=1),
                'date_to': today,
                'status': 'prepared',
                'generated_by': user,
                'generated_at': timezone.now(),
                'visibility': 'regulated_evidence',
            },
        )
        models.EvidencePackageEntry.objects.update_or_create(
            package=evidence_package,
            object_type='suppliercapa',
            object_id='CAPA-CN-0001',
            defaults={'label': 'CAPA evidence summary'},
        )
        evidence_package.checksum = evidence_package.calculate_checksum()
        evidence_package.save(update_fields=['checksum'])

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
                'visibility': 'customer_shared',
            },
        )

        self.stdout.write(self.style.SUCCESS(
            f'MedSupplier demo seeded for organization {org.name} ({org.slug}). '
            f'Accounts: {account.account_code}, {private_account.account_code}. '
            f'User: {user.email}'
        ))
