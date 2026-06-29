from decimal import Decimal
import csv
from io import StringIO
from django.conf import settings
from django.db.models import Avg, Count
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.utils.html import escape
from django.utils.dateparse import parse_date
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework import permissions, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from authentication.models import UserProfile
from core.organization_scoping import OrganizationScopedViewSetMixin
from integration.client import admin_apps_client

from . import models, serializers
from .permissions import (
    PRIVATE_VISIBILITIES,
    assert_can_mutate,
    assert_object_allowed,
    filter_queryset_for_context,
    resolve_medsupplier_context,
)


PRIVATE_VISIBLE_ROLES = ['org_admin', 'iso_manager', 'user']
SENSITIVE_ACTIONS = {'approve', 'reject', 'close', 'export', 'prepare', 'status_change'}


def _request_ip_address(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _safe_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    if hasattr(value, 'url'):
        try:
            return value.url
        except ValueError:
            return ''
    return str(value)


def _snapshot(instance):
    values = model_to_dict(instance)
    values['id'] = instance.pk
    values['organization'] = getattr(instance, 'organization_id', None)
    hidden = {
        'private_margin_notes', 'supplier_cost', 'margin', 'commission',
        'advance', 'internal_notes',
    }
    return {key: _safe_value(value) for key, value in values.items() if key not in hidden}


def _record_account(instance):
    if isinstance(instance, models.SupplierAccount):
        return instance
    account = getattr(instance, 'account', None)
    if account:
        return account
    document = getattr(instance, 'document', None)
    if document:
        return getattr(document, 'account', None)
    return None


def _record_label(instance):
    for field in (
        'account_code', 'full_name', 'title', 'requirement_id', 'document_number',
        'rfq_number', 'quote_number', 'po_number', 'lot_number', 'shipment_number',
        'inspection_number', 'event_number', 'capa_number', 'fmea_number', 'package_number',
    ):
        value = getattr(instance, field, None)
        if value:
            return value
    return str(instance.pk)


class MedSupplierCanEdit(permissions.BasePermission):
    message = 'No tienes permisos para editar ISO Smart MedSupplier.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
            organization_id = (
                request.query_params.get('organization_id')
                or request.query_params.get('organization')
                or getattr(request, 'organization_id', None)
            )
            context = resolve_medsupplier_context(request.user, organization_id)
            return context.can_mutate and context.is_supplier
        except Exception:
            return False


class MedSupplierScopedViewSet(OrganizationScopedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, MedSupplierCanEdit]

    def get_medsupplier_context(self):
        organization_id = self.get_organization_id()
        return resolve_medsupplier_context(self.request.user, organization_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['medsupplier_context'] = self.get_medsupplier_context()
        return context

    def _user_role(self, organization_id):
        role = getattr(self.request, 'user_role', None)
        if role:
            return role
        profile = UserProfile.objects.filter(
            user=self.request.user,
            organization_id=organization_id,
            is_active=True,
        ).first()
        return profile.role if profile else None

    def get_queryset(self):
        queryset = super().get_queryset()
        return filter_queryset_for_context(queryset, self.get_medsupplier_context())

    def get_organization_id(self):
        organization_id = super().get_organization_id()
        resolve_medsupplier_context(self.request.user, organization_id)
        return organization_id

    def perform_create(self, serializer):
        organization_id = self.get_organization_id()
        context = self.get_medsupplier_context()
        assert_can_mutate(context)
        instance = serializer.save(
            organization_id=organization_id,
            created_by=self.request.user,
            updated_by=self.request.user,
        )
        self._create_audit_event(instance, 'create', new_values=_snapshot(instance))

    def perform_update(self, serializer):
        self.get_organization_id()
        context = self.get_medsupplier_context()
        assert_can_mutate(context)
        assert_object_allowed(serializer.instance, context)
        old_values = _snapshot(serializer.instance)
        instance = serializer.save(updated_by=self.request.user)
        self._create_audit_event(instance, 'update', old_values=old_values, new_values=_snapshot(instance))

    def perform_destroy(self, instance):
        context = self.get_medsupplier_context()
        assert_can_mutate(context)
        assert_object_allowed(instance, context)
        old_values = _snapshot(instance)
        self._create_audit_event(instance, 'delete', old_values=old_values)
        instance.delete()

    def _create_audit_event(self, instance, action, old_values=None, new_values=None, reason=''):
        return models.MedSupplierAuditEvent.objects.create(
            organization_id=instance.organization_id,
            account=_record_account(instance),
            user=self.request.user if self.request.user.is_authenticated else None,
            action=action,
            record_type=instance._meta.model_name,
            record_id=str(instance.pk),
            object_type=instance._meta.label_lower,
            object_id=str(instance.pk),
            description=f'{action} {_record_label(instance)}',
            reason=reason or '',
            old_values=old_values or {},
            new_values=new_values or {},
            ip_address=_request_ip_address(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
        )

    def _require_reason(self):
        reason = (self.request.data.get('reason') or '').strip()
        if not reason:
            raise ValidationError({'reason': 'La razón es obligatoria para acciones sensibles/e-signature.'})
        return reason

    def _create_esignature(self, instance, meaning, reason):
        return models.MedSupplierESignature.objects.create(
            organization_id=instance.organization_id,
            account=_record_account(instance),
            user=self.request.user,
            meaning=meaning,
            reason=reason,
            object_type=instance._meta.label_lower,
            object_id=str(instance.pk),
            ip_address=_request_ip_address(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
        )

    def _apply_business_update(self, instance, updates, description=None, reason='', signature_meaning='status_change'):
        context = self.get_medsupplier_context()
        assert_can_mutate(context)
        assert_object_allowed(instance, context)
        old_values = _snapshot(instance)
        for field, value in updates.items():
            setattr(instance, field, value)
        if hasattr(instance, 'updated_by'):
            instance.updated_by = self.request.user
        instance.save()
        self._create_audit_event(
            instance,
            'status_change',
            old_values=old_values,
            new_values=_snapshot(instance),
            reason=reason,
        )
        if reason:
            self._create_esignature(instance, signature_meaning, reason)
        if description:
            latest = models.MedSupplierAuditEvent.objects.filter(
                organization=instance.organization,
                record_type=instance._meta.model_name,
                record_id=str(instance.pk),
            ).first()
            if latest:
                latest.description = description
                latest.save(update_fields=['description'])
        return instance


class ReadOnlyMedSupplierViewSet(OrganizationScopedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_medsupplier_context(self):
        organization_id = self.get_organization_id()
        return resolve_medsupplier_context(self.request.user, organization_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['medsupplier_context'] = self.get_medsupplier_context()
        return context

    def get_organization_id(self):
        organization_id = super().get_organization_id()
        resolve_medsupplier_context(self.request.user, organization_id)
        return organization_id

    def get_queryset(self):
        queryset = super().get_queryset()
        return filter_queryset_for_context(queryset, self.get_medsupplier_context())


class SupplierAccountViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierAccount.objects.all()
    serializer_class = serializers.SupplierAccountSerializer
    filterset_fields = ['status', 'risk_level', 'visibility', 'regulated_industry']
    search_fields = ['name', 'legal_name', 'account_code', 'primary_contact_email']
    ordering_fields = ['name', 'created_at', 'updated_at', 'next_qbr_date']

    @action(detail=True, methods=['post'], url_path='generate-qbr')
    def generate_qbr(self, request, pk=None):
        account = self.get_object()
        today = timezone.now().date()
        period_start = parse_date(request.data.get('period_start', '')) or today.replace(day=1)
        period_end = parse_date(request.data.get('period_end', '')) or today
        open_quality_events = models.SupplierQualityEvent.objects.filter(
            organization=account.organization,
            account=account,
        ).exclude(status='closed').count()
        risk_penalty = {
            'low': Decimal('0'),
            'medium': Decimal('5'),
            'high': Decimal('10'),
            'critical': Decimal('20'),
        }.get(account.risk_level, Decimal('5'))
        default_quality = max(Decimal('60'), Decimal('95') - risk_penalty - Decimal(open_quality_events * 3))
        default_delivery = Decimal('90')
        default_responsiveness = Decimal('92')
        default_overall = (default_quality + default_delivery + default_responsiveness) / Decimal('3')
        defaults = {
            'organization': account.organization,
            'quality_score': Decimal(str(request.data.get('quality_score', default_quality) or default_quality)),
            'delivery_score': Decimal(str(request.data.get('delivery_score', default_delivery) or default_delivery)),
            'responsiveness_score': Decimal(str(request.data.get('responsiveness_score', default_responsiveness) or default_responsiveness)),
            'overall_score': Decimal(str(request.data.get('overall_score', default_overall.quantize(Decimal('0.01'))) or default_overall)),
            'qbr_notes': request.data.get('qbr_notes', 'QBR generado desde Cliente 360.'),
            'visibility': request.data.get('visibility', 'shared'),
            'created_by': request.user,
            'updated_by': request.user,
        }
        existing = models.SupplierScorecard.objects.filter(
            account=account,
            period_start=period_start,
            period_end=period_end,
        ).first()
        old_values = _snapshot(existing) if existing else None
        scorecard, created = models.SupplierScorecard.objects.update_or_create(
            account=account,
            period_start=period_start,
            period_end=period_end,
            defaults=defaults,
        )
        self._create_audit_event(
            scorecard,
            'create' if created else 'update',
            old_values=old_values,
            new_values=_snapshot(scorecard),
        )
        return Response(serializers.SupplierScorecardSerializer(scorecard).data)


class SupplierContactViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierContact.objects.select_related('account')
    serializer_class = serializers.SupplierContactSerializer
    filterset_fields = ['account', 'is_customer_user', 'is_active', 'visibility']
    search_fields = ['full_name', 'email', 'role_title', 'department']


class SupplierMeetingViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierMeeting.objects.select_related('account')
    serializer_class = serializers.SupplierMeetingSerializer
    filterset_fields = ['account', 'status', 'visibility']
    search_fields = ['title', 'agenda', 'minutes']


class SupplierActionViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierAction.objects.select_related('account', 'meeting')
    serializer_class = serializers.SupplierActionSerializer
    filterset_fields = ['account', 'meeting', 'status', 'visibility']
    search_fields = ['title', 'owner', 'description']


class SupplierRequirementViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierRequirement.objects.select_related('account')
    serializer_class = serializers.SupplierRequirementSerializer
    filterset_fields = ['account', 'status', 'requirement_type', 'visibility']
    search_fields = ['requirement_id', 'title', 'description', 'source_reference']


class SupplierDocumentViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierDocument.objects.select_related('account')
    serializer_class = serializers.SupplierDocumentSerializer
    filterset_fields = ['account', 'status', 'document_type', 'visibility']
    search_fields = ['document_number', 'title', 'owner']

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        reason = self._require_reason()
        document = self.get_object()
        if document.status == 'obsolete':
            raise ValidationError({'status': 'No se puede aprobar un documento obsoleto.'})
        if document.status == 'effective':
            raise ValidationError({'status': 'El documento ya esta vigente.'})
        updates = {
            'status': 'effective',
            'effective_date': document.effective_date or timezone.now().date(),
        }
        document = self._apply_business_update(
            document,
            updates,
            f'approve document {_record_label(document)}',
            reason=reason,
            signature_meaning='approval',
        )
        version, _ = models.SupplierDocumentVersion.objects.get_or_create(
            organization=document.organization,
            document=document,
            revision=document.current_revision,
            defaults={
                'change_reason': reason,
                'visibility': document.visibility,
                'created_by': request.user,
                'updated_by': request.user,
            },
        )
        version.approved_by = request.user.get_full_name() or request.user.email
        version.approved_at = timezone.now()
        version.updated_by = request.user
        if not version.change_reason:
            version.change_reason = reason
        version.save(update_fields=['approved_by', 'approved_at', 'updated_by', 'updated_at', 'change_reason'])
        return Response(self.get_serializer(document).data)

    @action(detail=True, methods=['post'], url_path='obsolete')
    def obsolete(self, request, pk=None):
        reason = self._require_reason()
        document = self.get_object()
        if document.status == 'obsolete':
            raise ValidationError({'status': 'El documento ya esta obsoleto.'})
        document = self._apply_business_update(
            document,
            {
                'status': 'obsolete',
                'obsolete_date': timezone.now().date(),
            },
            f'obsolete document {_record_label(document)}',
            reason=reason,
            signature_meaning='status_change',
        )
        return Response(self.get_serializer(document).data)


class SupplierDocumentVersionViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierDocumentVersion.objects.select_related('document', 'document__account')
    serializer_class = serializers.SupplierDocumentVersionSerializer
    filterset_fields = ['document', 'revision', 'visibility']
    search_fields = ['revision', 'change_reason', 'approved_by']


class SupplierRFQViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierRFQ.objects.select_related('account').prefetch_related('requirements')
    serializer_class = serializers.SupplierRFQSerializer
    filterset_fields = ['account', 'status', 'visibility']
    search_fields = ['rfq_number', 'title', 'notes']

    @action(detail=True, methods=['post'], url_path='send')
    def send(self, request, pk=None):
        rfq = self.get_object()
        if rfq.status in ['sent', 'quoted', 'closed', 'cancelled']:
            raise ValidationError({'status': 'La RFQ no se puede enviar desde su estado actual.'})
        rfq = self._apply_business_update(rfq, {'status': 'sent'}, f'send RFQ {_record_label(rfq)}')
        return Response(self.get_serializer(rfq).data)


class SupplierQuoteViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierQuote.objects.select_related('account', 'rfq')
    serializer_class = serializers.SupplierQuoteSerializer
    filterset_fields = ['account', 'rfq', 'status', 'visibility']
    search_fields = ['quote_number', 'private_margin_notes']

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        reason = self._require_reason()
        quote = self.get_object()
        if quote.status in ['approved', 'rejected', 'expired']:
            raise ValidationError({'status': 'La cotizacion no se puede aprobar desde su estado actual.'})
        if quote.valid_until and quote.valid_until < timezone.now().date():
            raise ValidationError({'valid_until': 'No se puede aprobar una cotizacion expirada.'})
        if not quote.lines.exists():
            raise ValidationError({'lines': 'No se puede aprobar una cotización sin líneas.'})
        quote = self._apply_business_update(
            quote,
            {'status': 'approved'},
            f'approve quote {_record_label(quote)}',
            reason=reason,
            signature_meaning='approval',
        )
        return Response(self.get_serializer(quote).data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        reason = self._require_reason()
        quote = self.get_object()
        if quote.status in ['approved', 'rejected', 'expired']:
            raise ValidationError({'status': 'La cotizacion no se puede rechazar desde su estado actual.'})
        quote = self._apply_business_update(
            quote,
            {'status': 'rejected'},
            f'reject quote {_record_label(quote)}',
            reason=reason,
            signature_meaning='status_change',
        )
        return Response(self.get_serializer(quote).data)

    @action(detail=True, methods=['post'], url_path='revise')
    def revise(self, request, pk=None):
        reason = self._require_reason()
        quote = self.get_object()
        context = self.get_medsupplier_context()
        assert_can_mutate(context)
        assert_object_allowed(quote, context)

        base_revision = int((quote.metadata or {}).get('revision', 1))
        revision = base_revision + 1
        quote_number = f'{quote.quote_number}-R{revision}'
        while models.SupplierQuote.objects.filter(
            organization=quote.organization,
            quote_number=quote_number,
        ).exists():
            revision += 1
            quote_number = f'{quote.quote_number}-R{revision}'

        new_quote = models.SupplierQuote.objects.create(
            organization=quote.organization,
            account=quote.account,
            rfq=quote.rfq,
            quote_number=quote_number,
            status='draft',
            currency=quote.currency,
            total_amount=quote.total_amount,
            valid_until=parse_date(request.data.get('valid_until', '')) or quote.valid_until,
            private_margin_notes=quote.private_margin_notes,
            supplier_cost=quote.supplier_cost,
            margin=quote.margin,
            commission=quote.commission,
            advance=quote.advance,
            internal_notes=quote.internal_notes,
            forecast_probability=quote.forecast_probability,
            visibility=quote.visibility,
            metadata={
                **(quote.metadata or {}),
                'revision': revision,
                'previous_quote_id': quote.id,
                'revision_reason': reason,
            },
            created_by=request.user,
            updated_by=request.user,
        )
        for line in quote.lines.all().order_by('line_number'):
            models.SupplierQuoteLine.objects.create(
                organization=line.organization,
                quote=new_quote,
                rfq=line.rfq,
                account=line.account,
                line_number=line.line_number,
                product_code=line.product_code,
                description=line.description,
                technical_description=line.technical_description,
                quantity=line.quantity,
                uom=line.uom,
                moq=line.moq,
                lead_time_days=line.lead_time_days,
                tooling=line.tooling,
                incoterm=line.incoterm,
                unit_price=line.unit_price,
                supplier_cost=line.supplier_cost,
                margin=line.margin,
                currency=line.currency,
                valid_until=line.valid_until,
                taxes_and_charges=line.taxes_and_charges,
                customer_notes=line.customer_notes,
                internal_notes=line.internal_notes,
                visibility=line.visibility,
                metadata=line.metadata,
                created_by=request.user,
                updated_by=request.user,
            )
        self._create_audit_event(
            quote,
            'status_change',
            old_values=_snapshot(quote),
            new_values={'revised_quote_id': new_quote.id, 'revision': revision},
            reason=reason,
        )
        self._create_esignature(quote, 'status_change', reason)
        return Response(self.get_serializer(new_quote).data, status=201)


class SupplierQuoteLineViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierQuoteLine.objects.select_related('account', 'quote', 'rfq')
    serializer_class = serializers.SupplierQuoteLineSerializer
    filterset_fields = ['account', 'quote', 'rfq', 'visibility']
    search_fields = ['product_code', 'description', 'technical_description', 'customer_notes', 'internal_notes']


class SupplierPurchaseOrderViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierPurchaseOrder.objects.select_related('account', 'quote')
    serializer_class = serializers.SupplierPurchaseOrderSerializer
    filterset_fields = ['account', 'quote', 'status', 'visibility']
    search_fields = ['po_number']

    @action(detail=True, methods=['post'], url_path='close')
    def close(self, request, pk=None):
        reason = self._require_reason()
        purchase_order = self.get_object()
        if purchase_order.status in ['closed', 'cancelled']:
            raise ValidationError({'status': 'La orden no se puede cerrar desde su estado actual.'})
        purchase_order = self._apply_business_update(
            purchase_order,
            {'status': 'closed'},
            f'close PO {_record_label(purchase_order)}',
            reason=reason,
            signature_meaning='closure',
        )
        return Response(self.get_serializer(purchase_order).data)

    @action(detail=True, methods=['get'], url_path='traceability')
    def traceability(self, request, pk=None):
        purchase_order = self.get_object()
        shipments = purchase_order.shipments.all().order_by('shipment_number')
        lots = purchase_order.lots.all().order_by('lot_number')
        inspections = models.SupplierInspection.objects.filter(
            organization=purchase_order.organization,
            shipment__in=shipments,
        ).order_by('inspection_number')
        return Response({
            'purchase_order': self.get_serializer(purchase_order).data,
            'lines': serializers.SupplierOrderLineSerializer(
                purchase_order.lines.all().order_by('line_number'),
                many=True,
                context=self.get_serializer_context(),
            ).data,
            'lots': serializers.SupplierLotSerializer(
                lots,
                many=True,
                context=self.get_serializer_context(),
            ).data,
            'shipments': serializers.SupplierShipmentSerializer(
                shipments,
                many=True,
                context=self.get_serializer_context(),
            ).data,
            'inspections': serializers.SupplierInspectionSerializer(
                inspections,
                many=True,
                context=self.get_serializer_context(),
            ).data,
        })


class SupplierOrderLineViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierOrderLine.objects.select_related('account', 'purchase_order', 'quote_line')
    serializer_class = serializers.SupplierOrderLineSerializer
    filterset_fields = ['account', 'purchase_order', 'quote_line', 'status', 'visibility']
    search_fields = ['product_code', 'description', 'discrepancy_notes']


class SupplierLotViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierLot.objects.select_related('account', 'purchase_order')
    serializer_class = serializers.SupplierLotSerializer
    filterset_fields = ['account', 'purchase_order', 'product_code', 'visibility']
    search_fields = ['lot_number', 'product_code', 'product_description']


class SupplierShipmentViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierShipment.objects.select_related('account', 'purchase_order')
    serializer_class = serializers.SupplierShipmentSerializer
    filterset_fields = ['account', 'purchase_order', 'status', 'visibility']
    search_fields = ['shipment_number', 'carrier', 'tracking_number']


class SupplierShipmentMilestoneViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierShipmentMilestone.objects.select_related('account', 'shipment')
    serializer_class = serializers.SupplierShipmentMilestoneSerializer
    filterset_fields = ['account', 'shipment', 'status', 'milestone_type', 'visibility']
    search_fields = ['milestone_type', 'carrier', 'tracking_number', 'incident_notes', 'delay_reason']


class SupplierInspectionViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierInspection.objects.select_related('account', 'shipment')
    serializer_class = serializers.SupplierInspectionSerializer
    filterset_fields = ['account', 'shipment', 'result', 'visibility']
    search_fields = ['inspection_number', 'inspected_by', 'findings']


class SupplierQualityEventViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierQualityEvent.objects.select_related('account', 'inspection')
    serializer_class = serializers.SupplierQualityEventSerializer
    filterset_fields = ['account', 'inspection', 'event_type', 'severity', 'status', 'visibility']
    search_fields = ['event_number', 'title', 'description', 'owner']

    @action(detail=True, methods=['post'], url_path='close')
    def close(self, request, pk=None):
        reason = self._require_reason()
        quality_event = self.get_object()
        if quality_event.status == 'closed':
            raise ValidationError({'status': 'El evento de calidad ya esta cerrado.'})
        if quality_event.capas.exclude(status__in=['closed', 'cancelled']).exists():
            raise ValidationError({'capas': 'No se puede cerrar el evento mientras tenga CAPA abierta.'})
        quality_event = self._apply_business_update(
            quality_event,
            {'status': 'closed'},
            f'close quality event {_record_label(quality_event)}',
            reason=reason,
            signature_meaning='closure',
        )
        return Response(self.get_serializer(quality_event).data)


class SupplierCAPAViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierCAPA.objects.select_related('account', 'quality_event')
    serializer_class = serializers.SupplierCAPASerializer
    filterset_fields = ['account', 'quality_event', 'status', 'visibility']
    search_fields = ['capa_number', 'root_cause', 'corrective_action', 'preventive_action', 'owner']

    @action(detail=True, methods=['post'], url_path='close')
    def close(self, request, pk=None):
        reason = self._require_reason()
        capa = self.get_object()
        if capa.status in ['closed', 'cancelled']:
            raise ValidationError({'status': 'La CAPA no se puede cerrar desde su estado actual.'})
        missing = {}
        if not (capa.root_cause or '').strip():
            missing['root_cause'] = 'Se requiere causa raíz para cerrar la CAPA.'
        if not ((capa.corrective_action or '').strip() or (capa.preventive_action or '').strip()):
            missing['corrective_action'] = 'Se requiere acción correctiva o preventiva para cerrar la CAPA.'
        if not (capa.effectiveness_result or '').strip():
            missing['effectiveness_result'] = 'Se requiere resultado de efectividad para cerrar la CAPA.'
        if not (capa.evidence_summary or '').strip():
            missing['evidence_summary'] = 'Se requiere evidencia o resumen de evidencia para cerrar la CAPA.'
        if missing:
            raise ValidationError(missing)
        capa = self._apply_business_update(
            capa,
            {'status': 'closed'},
            f'close CAPA {_record_label(capa)}',
            reason=reason,
            signature_meaning='closure',
        )
        return Response(self.get_serializer(capa).data)

    @action(detail=True, methods=['post'], url_path='add-action')
    def add_action(self, request, pk=None):
        capa = self.get_object()
        context = self.get_medsupplier_context()
        assert_can_mutate(context)
        assert_object_allowed(capa, context)
        action_text = (request.data.get('action') or '').strip()
        if not action_text:
            raise ValidationError({'action': 'La acción CAPA es obligatoria.'})
        owner = (request.data.get('owner') or '').strip()
        due_date = request.data.get('due_date') or ''
        old_values = _snapshot(capa)
        actions = list((capa.metadata or {}).get('actions', []))
        entry = {
            'sequence': len(actions) + 1,
            'action': action_text,
            'owner': owner,
            'due_date': due_date,
            'status': request.data.get('status') or 'open',
            'created_at': timezone.now().isoformat(),
            'created_by': request.user.email,
        }
        actions.append(entry)
        capa.metadata = {**(capa.metadata or {}), 'actions': actions}
        capa.updated_by = request.user
        capa.save(update_fields=['metadata', 'updated_by', 'updated_at'])
        self._create_audit_event(
            capa,
            'update',
            old_values=old_values,
            new_values=_snapshot(capa),
            reason=request.data.get('reason', ''),
        )
        return Response({'actions': actions, 'capa': self.get_serializer(capa).data}, status=201)


class SupplierFMEAViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierFMEA.objects.select_related('account')
    serializer_class = serializers.SupplierFMEASerializer
    filterset_fields = ['account', 'status', 'visibility']
    search_fields = ['fmea_number', 'title', 'process', 'owner', 'notes']


class SupplierFMEAItemViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierFMEAItem.objects.select_related('account', 'fmea', 'quality_event', 'capa', 'document')
    serializer_class = serializers.SupplierFMEAItemSerializer
    filterset_fields = ['account', 'fmea', 'status', 'visibility']
    search_fields = ['hazard', 'failure_mode', 'cause', 'effect', 'mitigation', 'residual_risk']


class SupplierScorecardViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierScorecard.objects.select_related('account')
    serializer_class = serializers.SupplierScorecardSerializer
    filterset_fields = ['account', 'visibility']


class MedSupplierAuditEventViewSet(ReadOnlyMedSupplierViewSet):
    queryset = models.MedSupplierAuditEvent.objects.select_related('account', 'user')
    serializer_class = serializers.MedSupplierAuditEventSerializer
    filterset_fields = ['account', 'action', 'record_type']
    search_fields = ['description', 'reason', 'record_type', 'record_id']

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        export_format = (
            request.query_params.get('file_format')
            or request.query_params.get('format')
            or 'json'
        ).lower()
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset[:1000], many=True)
        if export_format == 'csv':
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['created_at', 'action', 'record_type', 'record_id', 'description', 'reason', 'event_hash'])
            for event in queryset[:1000]:
                writer.writerow([
                    event.created_at.isoformat(), event.action, event.record_type,
                    event.record_id, event.description, event.reason, event.event_hash,
                ])
            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="medsupplier-audit-events.csv"'
            return response
        return Response({'count': queryset.count(), 'results': serializer.data})


class MedSupplierESignatureViewSet(ReadOnlyMedSupplierViewSet):
    queryset = models.MedSupplierESignature.objects.select_related('account', 'user')
    serializer_class = serializers.MedSupplierESignatureSerializer
    filterset_fields = ['account', 'meaning', 'object_type', 'object_id']
    search_fields = ['reason', 'object_type', 'object_id']


class EvidencePackageViewSet(MedSupplierScopedViewSet):
    queryset = models.EvidencePackage.objects.select_related('account', 'generated_by').prefetch_related('entries')
    serializer_class = serializers.EvidencePackageSerializer
    filterset_fields = ['account', 'status', 'visibility']
    search_fields = ['package_number', 'title', 'scope']

    @action(detail=True, methods=['post'], url_path='prepare')
    def prepare(self, request, pk=None):
        package = self.get_object()
        if not package.entries.exists():
            raise ValidationError({'entries': 'No se puede preparar un evidence package vacío.'})
        package.generated_by = request.user
        package.generated_at = timezone.now()
        package.status = 'prepared'
        package.checksum = package.calculate_checksum()
        package.updated_by = request.user
        package.save(update_fields=['generated_by', 'generated_at', 'status', 'checksum', 'updated_by', 'updated_at'])
        self._create_audit_event(package, 'status_change', new_values=_snapshot(package), reason='Evidence package prepared')
        return Response(self.get_serializer(package).data)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        reason = self._require_reason()
        package = self.get_object()
        if not package.entries.exists():
            raise ValidationError({'entries': 'No se puede aprobar un evidence package vacío.'})
        package = self._apply_business_update(
            package,
            {
                'status': 'approved',
                'generated_by': request.user,
                'generated_at': package.generated_at or timezone.now(),
                'checksum': package.calculate_checksum(),
            },
            f'approve evidence package {_record_label(package)}',
            reason=reason,
            signature_meaning='approval',
        )
        return Response(self.get_serializer(package).data)

    @action(detail=True, methods=['get'], url_path='export')
    def export(self, request, pk=None):
        package = self.get_object()
        if not package.entries.exists():
            raise ValidationError({'entries': 'No se puede exportar un evidence package vacío.'})
        data = self.get_serializer(package).data
        self._create_audit_event(package, 'export', new_values={'package': data}, reason='Evidence package export')
        export_format = (
            request.query_params.get('file_format')
            or request.query_params.get('format')
            or 'json'
        ).lower()
        if export_format == 'html':
            rows = ''.join(
                '<tr>'
                f'<td>{escape(entry["object_type"])}</td>'
                f'<td>{escape(entry["object_id"])}</td>'
                f'<td>{escape(entry.get("label") or "")}</td>'
                '</tr>'
                for entry in data['entries']
            )
            html = (
                '<!doctype html><html><head><meta charset="utf-8">'
                f'<title>{escape(package.package_number)} Evidence Package</title>'
                '</head><body>'
                f'<h1>{escape(package.title)}</h1>'
                f'<p>Package: {escape(package.package_number)} | Version: {escape(package.version)} | '
                f'Status: {escape(package.status)} | Checksum: {escape(package.checksum or "")}</p>'
                '<table><thead><tr><th>Object type</th><th>Object ID</th><th>Label</th></tr></thead>'
                f'<tbody>{rows}</tbody></table>'
                '</body></html>'
            )
            response = HttpResponse(html, content_type='text/html')
            response['Content-Disposition'] = f'attachment; filename="{package.package_number}.html"'
            return response
        return Response(data)

    @action(detail=True, methods=['get'], url_path='index')
    def index(self, request, pk=None):
        package = self.get_object()
        entries = package.entries.all().order_by('object_type', 'object_id')
        grouped = {}
        for entry in entries:
            grouped.setdefault(entry.object_type, []).append({
                'object_id': entry.object_id,
                'label': entry.label,
                'metadata': entry.metadata,
                'added_at': entry.added_at,
            })
        return Response({
            'package_number': package.package_number,
            'status': package.status,
            'checksum': package.checksum,
            'entry_count': entries.count(),
            'objects': grouped,
        })


class EvidencePackageEntryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, MedSupplierCanEdit]
    queryset = models.EvidencePackageEntry.objects.select_related('package', 'package__account')
    serializer_class = serializers.EvidencePackageEntrySerializer
    filterset_fields = ['package', 'object_type', 'object_id']

    def get_organization_id(self):
        value = self.request.query_params.get('organization_id') or getattr(self.request, 'organization_id', None)
        if not value:
            raise ValidationError({'organization_id': 'organization_id requerido'})
        return int(value)

    def get_medsupplier_context(self):
        return resolve_medsupplier_context(self.request.user, self.get_organization_id())

    def get_queryset(self):
        queryset = super().get_queryset().filter(package__organization_id=self.get_organization_id())
        context = self.get_medsupplier_context()
        if context.is_customer:
            queryset = queryset.filter(package__account_id__in=context.account_ids)
        return queryset

    def perform_create(self, serializer):
        package = serializer.validated_data['package']
        context = self.get_medsupplier_context()
        assert_can_mutate(context)
        assert_object_allowed(package, context)
        serializer.save()


def _resolve_organization_id(request):
    value = request.query_params.get('organization_id') or getattr(request, 'organization_id', None)
    if not value:
        return None
    return int(value)


def _user_can_access_organization(user, organization_id):
    try:
        resolve_medsupplier_context(user, organization_id)
        return True
    except PermissionDenied:
        return False


def _get_user_profile(user, organization_id):
    return UserProfile.objects.select_related('organization').filter(
        user=user,
        organization_id=organization_id,
        is_active=True,
    ).first()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def effective_permissions(request):
    organization_id = _resolve_organization_id(request)
    if not organization_id:
        return Response({'organization_id': 'organization_id requerido'}, status=400)
    context = resolve_medsupplier_context(request.user, organization_id)
    return Response({
        'organization_id': context.organization_id,
        'side': context.side,
        'role': context.role,
        'account_ids': list(context.account_ids),
        'source': context.source,
        'permissions': {
            'can_mutate': context.can_mutate,
            'can_view_private_financials': context.can_view_private_financials,
            'can_access_supplier_cockpit': context.can_access_supplier_cockpit,
            'is_read_only': context.is_read_only,
        },
        'visible_visibilities': sorted(context.visible_visibilities),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_summary(request):
    organization_id = _resolve_organization_id(request)
    if not organization_id:
        return Response({'organization_id': 'organization_id requerido'}, status=400)
    context = resolve_medsupplier_context(request.user, organization_id)

    accounts = filter_queryset_for_context(models.SupplierAccount.objects.all(), context)
    quality_events = filter_queryset_for_context(models.SupplierQualityEvent.objects.all(), context)
    actions = filter_queryset_for_context(models.SupplierAction.objects.all(), context)
    scorecards = filter_queryset_for_context(models.SupplierScorecard.objects.all(), context)
    rfqs = filter_queryset_for_context(models.SupplierRFQ.objects.all(), context)
    purchase_orders = filter_queryset_for_context(models.SupplierPurchaseOrder.objects.all(), context)
    shipments = filter_queryset_for_context(models.SupplierShipment.objects.all(), context)
    quotes = filter_queryset_for_context(models.SupplierQuote.objects.all(), context)

    return Response({
        'product': 'ISO Smart MedSupplier',
        'value_proposition': 'Torre de control regulada Supplier-Customer para clientes de Medical Devices y empresas transnacionales.',
        'organization_id': organization_id,
        'role': context.role,
        'side': context.side,
        'accounts': accounts.count(),
        'active_accounts': accounts.filter(status='active').count(),
        'open_actions': actions.exclude(status='closed').count(),
        'open_quality_events': quality_events.exclude(status='closed').count(),
        'overdue_actions': actions.exclude(status='closed').filter(due_date__lt=timezone.now().date()).count(),
        'rfqs': rfqs.count(),
        'purchase_orders': purchase_orders.count(),
        'shipments_in_transit': shipments.filter(status='in_transit').count(),
        'average_scorecard': scorecards.aggregate(avg=Avg('overall_score'))['avg'] or 0,
        'quality_events_by_status': list(
            quality_events.values('status').annotate(total=Count('id')).order_by('status')
        ),
        'private_records': (
            accounts.filter(visibility__in=PRIVATE_VISIBILITIES).count()
            + quotes.filter(visibility__in=PRIVATE_VISIBILITIES).count()
        ),
        'shared_records': accounts.exclude(visibility__in=PRIVATE_VISIBILITIES).count(),
        'risk_distribution': list(accounts.values('risk_level').annotate(total=Count('id')).order_by('risk_level')),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def private_cockpit(request):
    organization_id = _resolve_organization_id(request)
    if not organization_id:
        return Response({'organization_id': 'organization_id requerido'}, status=400)
    context = resolve_medsupplier_context(request.user, organization_id)
    if not context.can_access_supplier_cockpit:
        return Response({'detail': 'Cockpit privado disponible solo para Supplier Admin/Finance/Sales.'}, status=403)

    accounts = models.SupplierAccount.objects.filter(organization_id=organization_id)
    quotes = models.SupplierQuote.objects.filter(organization_id=organization_id)
    open_orders = models.SupplierPurchaseOrder.objects.filter(organization_id=organization_id).exclude(status__in=['closed', 'cancelled'])
    today = timezone.now().date()
    return Response({
        'organization_id': organization_id,
        'role': context.role,
        'opportunities': {
            'accounts': accounts.count(),
            'rfqs': models.SupplierRFQ.objects.filter(organization_id=organization_id).count(),
            'quotes_pending': quotes.filter(status__in=['draft', 'submitted']).count(),
            'orders_open': open_orders.count(),
        },
        'finance': {
            'quoted_total': quotes.aggregate(total=Count('id'))['total'] or 0,
            'supplier_cost_total': str(sum((quote.supplier_cost for quote in quotes), Decimal('0'))),
            'commission_total': str(sum((quote.commission for quote in quotes), Decimal('0'))),
            'advance_total': str(sum((quote.advance for quote in quotes), Decimal('0'))),
            'average_margin': str((quotes.aggregate(avg=Avg('margin'))['avg'] or Decimal('0')).quantize(Decimal('0.01'))),
        },
        'billing': {
            'open_order_count': open_orders.count(),
            'open_order_value': str(sum((order.total_amount for order in open_orders), Decimal('0'))),
            'approved_quote_value': str(sum((quote.total_amount for quote in quotes.filter(status='approved')), Decimal('0'))),
        },
        'forecast': list(
            quotes.exclude(status__in=['rejected', 'expired']).values(
                'id', 'quote_number', 'account_id', 'status', 'total_amount',
                'margin', 'forecast_probability', 'valid_until',
            ).order_by('valid_until')[:20]
        ),
        'internal_notes': list(
            quotes.exclude(internal_notes='').values(
                'id', 'quote_number', 'account_id', 'internal_notes', 'private_margin_notes',
            ).order_by('-updated_at')[:20]
        ),
        'commercial_risk': list(
            accounts.filter(risk_level__in=['high', 'critical']).values(
                'id', 'name', 'account_code', 'risk_level', 'status', 'next_qbr_date',
            )[:20]
        ),
        'aging': {
            'expired_quotes': quotes.filter(valid_until__lt=today).exclude(status__in=['rejected', 'expired']).count(),
            'orders_due': open_orders.filter(promised_ship_date__lt=today).count(),
        },
        'recent_accounts': list(accounts.order_by('-updated_at').values('id', 'name', 'account_code', 'updated_at')[:10]),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def integration_status(request):
    organization_id = _resolve_organization_id(request)
    if not organization_id:
        return Response({'organization_id': 'organization_id requerido'}, status=400)
    if not _user_can_access_organization(request.user, organization_id):
        return Response({'detail': 'No tienes acceso a esta organización'}, status=403)

    profile = _get_user_profile(request.user, organization_id)
    organization = profile.organization if profile else None
    adminapps_org_id = organization.external_id if organization and organization.external_id else organization_id

    health = admin_apps_client.health_check()
    product_access = admin_apps_client.validate_product_access(
        adminapps_org_id,
        'MEDSUPPLIER',
        use_cache=False,
    )

    return Response({
        'product': 'ISO Smart MedSupplier',
        'module_code': 'MEDSUPPLIER',
        'product_mode': getattr(settings, 'MEDSUPPLIER_PRODUCT_MODE', 'integrated'),
        'commercial_model': 'vendible_por_separado_o_junto_a_iso_smart',
        'adminapps_authority': {
            'organizations': True,
            'users': True,
            'roles': True,
            'entitlements': True,
            'product_access': True,
            'required_for_identity': settings.ADMIN_APPS_INTEGRATION.get('REQUIRE_IDENTITY_SOURCE', True),
        },
        'organization': {
            'id': organization_id,
            'name': getattr(organization, 'name', ''),
            'external_id': getattr(organization, 'external_id', None),
            'adminapps_lookup_id': adminapps_org_id,
        },
        'adminapps': {
            'available': 'error' not in health,
            'health': health,
            'product_access_source': product_access.get('source', 'adminapps'),
            'fallback': bool(product_access.get('fallback')),
        },
        'entitlement': {
            'enabled': bool(product_access.get('allowed')),
            'reason': product_access.get('reason'),
            'product': product_access.get('product'),
        },
        'iso_smart_integration': {
            'optional_commercial_bundle': True,
            'shares_identity_authority': True,
            'shares_qms_evidence_when_bundled': getattr(settings, 'MEDSUPPLIER_PRODUCT_MODE', 'integrated') == 'integrated',
        },
    })
