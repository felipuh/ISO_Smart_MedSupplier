from decimal import Decimal
from django.conf import settings
from django.db.models import Avg, Count
from django.forms.models import model_to_dict
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


PRIVATE_VISIBLE_ROLES = ['org_admin', 'iso_manager', 'user']


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
    return {key: _safe_value(value) for key, value in values.items()}


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
        'inspection_number', 'event_number', 'capa_number',
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

        role = getattr(request, 'user_role', None)
        if role:
            return role in ['org_admin', 'iso_manager', 'user']

        organization_id = (
            request.query_params.get('organization_id')
            or request.query_params.get('organization')
            or getattr(request, 'organization_id', None)
        )
        if not organization_id:
            return False
        return UserProfile.objects.filter(
            user=request.user,
            organization_id=organization_id,
            role__in=['org_admin', 'iso_manager', 'user'],
            is_active=True,
        ).exists()


class MedSupplierScopedViewSet(OrganizationScopedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, MedSupplierCanEdit]

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
        organization_id = self.get_organization_id()
        role = self._user_role(organization_id)
        if role in PRIVATE_VISIBLE_ROLES or self.request.user.is_superuser:
            return queryset
        model = getattr(queryset, 'model', None)
        if model and any(field.name == 'visibility' for field in model._meta.fields):
            return queryset.filter(visibility='shared')
        return queryset

    def get_organization_id(self):
        organization_id = super().get_organization_id()
        if self.request.user.is_superuser:
            return organization_id
        if not UserProfile.objects.filter(
            user=self.request.user,
            organization_id=organization_id,
            is_active=True,
        ).exists():
            raise PermissionDenied('No tienes acceso a esta organización')
        return organization_id

    def perform_create(self, serializer):
        organization_id = self.get_organization_id()
        instance = serializer.save(
            organization_id=organization_id,
            created_by=self.request.user,
            updated_by=self.request.user,
        )
        self._create_audit_event(instance, 'create', new_values=_snapshot(instance))

    def perform_update(self, serializer):
        self.get_organization_id()
        old_values = _snapshot(serializer.instance)
        instance = serializer.save(updated_by=self.request.user)
        self._create_audit_event(instance, 'update', old_values=old_values, new_values=_snapshot(instance))

    def perform_destroy(self, instance):
        old_values = _snapshot(instance)
        self._create_audit_event(instance, 'delete', old_values=old_values)
        instance.delete()

    def _create_audit_event(self, instance, action, old_values=None, new_values=None):
        models.MedSupplierAuditEvent.objects.create(
            organization_id=instance.organization_id,
            account=_record_account(instance),
            user=self.request.user if self.request.user.is_authenticated else None,
            action=action,
            record_type=instance._meta.model_name,
            record_id=str(instance.pk),
            description=f'{action} {_record_label(instance)}',
            old_values=old_values or {},
            new_values=new_values or {},
            ip_address=_request_ip_address(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
        )

    def _apply_business_update(self, instance, updates, description=None):
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
        )
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

    def get_organization_id(self):
        organization_id = super().get_organization_id()
        if self.request.user.is_superuser:
            return organization_id
        if not UserProfile.objects.filter(
            user=self.request.user,
            organization_id=organization_id,
            is_active=True,
        ).exists():
            raise PermissionDenied('No tienes acceso a esta organización')
        return organization_id

    def get_queryset(self):
        queryset = super().get_queryset()
        organization_id = self.get_organization_id()
        role = getattr(self.request, 'user_role', None)
        if not role:
            profile = UserProfile.objects.filter(
                user=self.request.user,
                organization_id=organization_id,
                is_active=True,
            ).first()
            role = profile.role if profile else None
        if role in PRIVATE_VISIBLE_ROLES or self.request.user.is_superuser:
            return queryset
        if queryset.model is models.MedSupplierAuditEvent:
            return queryset.filter(account__visibility='shared')
        return queryset


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
        document = self.get_object()
        if document.status == 'obsolete':
            raise ValidationError({'status': 'No se puede aprobar un documento obsoleto.'})
        if document.status == 'effective':
            raise ValidationError({'status': 'El documento ya esta vigente.'})
        updates = {
            'status': 'effective',
            'effective_date': document.effective_date or timezone.now().date(),
        }
        document = self._apply_business_update(document, updates, f'approve document {_record_label(document)}')
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
        quote = self.get_object()
        if quote.status in ['approved', 'rejected', 'expired']:
            raise ValidationError({'status': 'La cotizacion no se puede aprobar desde su estado actual.'})
        if quote.valid_until and quote.valid_until < timezone.now().date():
            raise ValidationError({'valid_until': 'No se puede aprobar una cotizacion expirada.'})
        quote = self._apply_business_update(quote, {'status': 'approved'}, f'approve quote {_record_label(quote)}')
        return Response(self.get_serializer(quote).data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        quote = self.get_object()
        if quote.status in ['approved', 'rejected', 'expired']:
            raise ValidationError({'status': 'La cotizacion no se puede rechazar desde su estado actual.'})
        quote = self._apply_business_update(quote, {'status': 'rejected'}, f'reject quote {_record_label(quote)}')
        return Response(self.get_serializer(quote).data)


class SupplierPurchaseOrderViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierPurchaseOrder.objects.select_related('account', 'quote')
    serializer_class = serializers.SupplierPurchaseOrderSerializer
    filterset_fields = ['account', 'quote', 'status', 'visibility']
    search_fields = ['po_number']

    @action(detail=True, methods=['post'], url_path='close')
    def close(self, request, pk=None):
        purchase_order = self.get_object()
        if purchase_order.status in ['closed', 'cancelled']:
            raise ValidationError({'status': 'La orden no se puede cerrar desde su estado actual.'})
        purchase_order = self._apply_business_update(
            purchase_order,
            {'status': 'closed'},
            f'close PO {_record_label(purchase_order)}',
        )
        return Response(self.get_serializer(purchase_order).data)


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
        quality_event = self.get_object()
        if quality_event.status == 'closed':
            raise ValidationError({'status': 'El evento de calidad ya esta cerrado.'})
        if quality_event.capas.exclude(status__in=['closed', 'cancelled']).exists():
            raise ValidationError({'capas': 'No se puede cerrar el evento mientras tenga CAPA abierta.'})
        quality_event = self._apply_business_update(
            quality_event,
            {'status': 'closed'},
            f'close quality event {_record_label(quality_event)}',
        )
        return Response(self.get_serializer(quality_event).data)


class SupplierCAPAViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierCAPA.objects.select_related('account', 'quality_event')
    serializer_class = serializers.SupplierCAPASerializer
    filterset_fields = ['account', 'quality_event', 'status', 'visibility']
    search_fields = ['capa_number', 'root_cause', 'corrective_action', 'preventive_action', 'owner']

    @action(detail=True, methods=['post'], url_path='close')
    def close(self, request, pk=None):
        capa = self.get_object()
        if capa.status in ['closed', 'cancelled']:
            raise ValidationError({'status': 'La CAPA no se puede cerrar desde su estado actual.'})
        if not (capa.effectiveness_result or '').strip():
            raise ValidationError({'effectiveness_result': 'Se requiere resultado de efectividad para cerrar la CAPA.'})
        capa = self._apply_business_update(capa, {'status': 'closed'}, f'close CAPA {_record_label(capa)}')
        return Response(self.get_serializer(capa).data)


class SupplierScorecardViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierScorecard.objects.select_related('account')
    serializer_class = serializers.SupplierScorecardSerializer
    filterset_fields = ['account', 'visibility']


class MedSupplierAuditEventViewSet(ReadOnlyMedSupplierViewSet):
    queryset = models.MedSupplierAuditEvent.objects.select_related('account', 'user')
    serializer_class = serializers.MedSupplierAuditEventSerializer
    filterset_fields = ['account', 'action', 'record_type']
    search_fields = ['description', 'reason', 'record_type', 'record_id']


def _resolve_organization_id(request):
    value = request.query_params.get('organization_id') or getattr(request, 'organization_id', None)
    if not value:
        return None
    return int(value)


def _user_can_access_organization(user, organization_id):
    if user.is_superuser:
        return True
    return UserProfile.objects.filter(user=user, organization_id=organization_id, is_active=True).exists()


def _get_user_profile(user, organization_id):
    return UserProfile.objects.select_related('organization').filter(
        user=user,
        organization_id=organization_id,
        is_active=True,
    ).first()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_summary(request):
    organization_id = _resolve_organization_id(request)
    if not organization_id:
        return Response({'organization_id': 'organization_id requerido'}, status=400)
    if not _user_can_access_organization(request.user, organization_id):
        return Response({'detail': 'No tienes acceso a esta organización'}, status=403)

    accounts = models.SupplierAccount.objects.filter(organization_id=organization_id)
    quality_events = models.SupplierQualityEvent.objects.filter(organization_id=organization_id)
    actions = models.SupplierAction.objects.filter(organization_id=organization_id)
    scorecards = models.SupplierScorecard.objects.filter(organization_id=organization_id)

    return Response({
        'product': 'ISO Smart MedSupplier',
        'value_proposition': 'Torre de control regulada Supplier-Customer para clientes de Medical Devices y empresas transnacionales.',
        'organization_id': organization_id,
        'accounts': accounts.count(),
        'active_accounts': accounts.filter(status='active').count(),
        'open_actions': actions.exclude(status='closed').count(),
        'open_quality_events': quality_events.exclude(status='closed').count(),
        'overdue_actions': actions.exclude(status='closed').filter(due_date__lt=timezone.now().date()).count(),
        'rfqs': models.SupplierRFQ.objects.filter(organization_id=organization_id).count(),
        'purchase_orders': models.SupplierPurchaseOrder.objects.filter(organization_id=organization_id).count(),
        'shipments_in_transit': models.SupplierShipment.objects.filter(
            organization_id=organization_id,
            status='in_transit',
        ).count(),
        'average_scorecard': scorecards.aggregate(avg=Avg('overall_score'))['avg'] or 0,
        'quality_events_by_status': list(
            quality_events.values('status').annotate(total=Count('id')).order_by('status')
        ),
        'private_records': (
            accounts.filter(visibility='private').count()
            + models.SupplierQuote.objects.filter(organization_id=organization_id, visibility='private').count()
        ),
        'shared_records': accounts.filter(visibility='shared').count(),
        'risk_distribution': list(accounts.values('risk_level').annotate(total=Count('id')).order_by('risk_level')),
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
    modules_result = admin_apps_client.get_organization_modules(adminapps_org_id, use_cache=False)
    modules = modules_result.get('modules') or []
    medsupplier_module = next(
        (module for module in modules if module.get('code') == 'MEDSUPPLIER'),
        None,
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
            'module_access': True,
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
            'modules_source': modules_result.get('source', 'adminapps'),
        },
        'entitlement': {
            'enabled': bool(medsupplier_module and medsupplier_module.get('enabled', True)),
            'module': medsupplier_module,
        },
        'iso_smart_integration': {
            'optional_commercial_bundle': True,
            'shares_identity_authority': True,
            'shares_qms_evidence_when_bundled': getattr(settings, 'MEDSUPPLIER_PRODUCT_MODE', 'integrated') == 'integrated',
        },
    })
