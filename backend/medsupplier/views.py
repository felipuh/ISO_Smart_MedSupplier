from django.conf import settings
from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from rest_framework import permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from authentication.models import UserProfile
from core.organization_scoping import OrganizationScopedViewSetMixin
from integration.client import admin_apps_client

from . import models, serializers


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
        serializer.save(
            organization_id=organization_id,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        self.get_organization_id()
        serializer.save(updated_by=self.request.user)


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


class SupplierAccountViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierAccount.objects.all()
    serializer_class = serializers.SupplierAccountSerializer
    filterset_fields = ['status', 'risk_level', 'visibility', 'regulated_industry']
    search_fields = ['name', 'legal_name', 'account_code', 'primary_contact_email']
    ordering_fields = ['name', 'created_at', 'updated_at', 'next_qbr_date']


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


class SupplierQuoteViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierQuote.objects.select_related('account', 'rfq')
    serializer_class = serializers.SupplierQuoteSerializer
    filterset_fields = ['account', 'rfq', 'status', 'visibility']
    search_fields = ['quote_number', 'private_margin_notes']


class SupplierPurchaseOrderViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierPurchaseOrder.objects.select_related('account', 'quote')
    serializer_class = serializers.SupplierPurchaseOrderSerializer
    filterset_fields = ['account', 'quote', 'status', 'visibility']
    search_fields = ['po_number']


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


class SupplierCAPAViewSet(MedSupplierScopedViewSet):
    queryset = models.SupplierCAPA.objects.select_related('account', 'quality_event')
    serializer_class = serializers.SupplierCAPASerializer
    filterset_fields = ['account', 'quality_event', 'status', 'visibility']
    search_fields = ['capa_number', 'root_cause', 'corrective_action', 'preventive_action', 'owner']


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
