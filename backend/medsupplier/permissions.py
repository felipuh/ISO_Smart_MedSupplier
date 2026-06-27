from dataclasses import dataclass

from rest_framework.exceptions import PermissionDenied

from authentication.models import UserProfile

from . import models


SUPPLIER_ROLES = {
    'supplier_admin',
    'supplier_sales',
    'supplier_finance',
    'supplier_quality',
    'supplier_logistics',
    'supplier_viewer',
}
CUSTOMER_ROLES = {
    'customer_admin',
    'customer_buyer',
    'customer_quality',
    'customer_logistics',
    'customer_auditor',
    'customer_viewer',
}
READ_ONLY_ROLES = {'supplier_viewer', 'customer_viewer', 'customer_auditor'}
PRIVATE_FINANCIAL_ROLES = {'supplier_admin', 'supplier_finance'}
SUPPLIER_COCKPIT_ROLES = {'supplier_admin', 'supplier_finance', 'supplier_sales'}
SUPPLIER_PRIVATE_ROLES = {
    'supplier_admin',
    'supplier_sales',
    'supplier_finance',
    'supplier_quality',
    'supplier_logistics',
}
QUALITY_ROLES = {'supplier_admin', 'supplier_quality', 'customer_quality', 'customer_auditor'}
LOGISTICS_ROLES = {'supplier_admin', 'supplier_logistics', 'customer_logistics'}

CUSTOMER_VISIBLE_VISIBILITIES = {'public_shared', 'customer_shared', 'regulated_evidence', 'shared'}
SUPPLIER_VISIBLE_VISIBILITIES = {
    'public_shared',
    'customer_shared',
    'supplier_private',
    'supplier_confidential',
    'regulated_evidence',
    'audit_only',
    'archived',
    'obsolete',
    'shared',
    'private',
}
PRIVATE_VISIBILITIES = {'supplier_private', 'supplier_confidential', 'audit_only', 'private'}


@dataclass(frozen=True)
class MedSupplierContext:
    organization_id: int
    side: str
    role: str
    account_ids: tuple
    source: str = 'medsupplier_scope'

    @property
    def is_supplier(self):
        return self.side == 'supplier'

    @property
    def is_customer(self):
        return self.side == 'customer'

    @property
    def is_read_only(self):
        return self.role in READ_ONLY_ROLES

    @property
    def can_mutate(self):
        return not self.is_read_only

    @property
    def can_view_private_financials(self):
        return self.role in PRIVATE_FINANCIAL_ROLES

    @property
    def can_access_supplier_cockpit(self):
        return self.role in SUPPLIER_COCKPIT_ROLES

    @property
    def visible_visibilities(self):
        return SUPPLIER_VISIBLE_VISIBILITIES if self.is_supplier else CUSTOMER_VISIBLE_VISIBILITIES

    def has_account_scope(self, account_id):
        if self.is_supplier:
            return True
        return int(account_id) in self.account_ids


def _fallback_context(user, organization_id):
    profile = UserProfile.objects.filter(
        user=user,
        organization_id=organization_id,
        is_active=True,
    ).first()
    if not profile:
        return None
    if profile.role in {'org_admin', 'iso_manager'}:
        return MedSupplierContext(
            organization_id=int(organization_id),
            side='supplier',
            role='supplier_admin',
            account_ids=(),
            source='user_profile_fallback',
        )
    if profile.role == 'auditor':
        return MedSupplierContext(
            organization_id=int(organization_id),
            side='customer',
            role='customer_auditor',
            account_ids=tuple(),
            source='user_profile_fallback',
        )
    if profile.role == 'viewer':
        return MedSupplierContext(
            organization_id=int(organization_id),
            side='supplier',
            role='supplier_viewer',
            account_ids=(),
            source='user_profile_fallback',
        )
    return None


def resolve_medsupplier_context(user, organization_id):
    if not user or not user.is_authenticated:
        raise PermissionDenied('Autenticación requerida.')
    if user.is_superuser:
        return MedSupplierContext(
            organization_id=int(organization_id),
            side='supplier',
            role='supplier_admin',
            account_ids=(),
            source='superuser',
        )

    scopes = list(
        models.MedSupplierUserScope.objects.filter(
            user=user,
            organization_id=organization_id,
            is_active=True,
        ).values('side', 'role', 'account_id')
    )
    if scopes:
        supplier_scope = next((scope for scope in scopes if scope['side'] == 'supplier'), None)
        if supplier_scope:
            return MedSupplierContext(
                organization_id=int(organization_id),
                side='supplier',
                role=supplier_scope['role'],
                account_ids=tuple(),
            )
        account_ids = tuple(sorted({scope['account_id'] for scope in scopes if scope['account_id']}))
        if not account_ids:
            raise PermissionDenied('El usuario Customer no tiene account_scope MedSupplier activo.')
        return MedSupplierContext(
            organization_id=int(organization_id),
            side='customer',
            role=scopes[0]['role'],
            account_ids=account_ids,
        )

    fallback = _fallback_context(user, organization_id)
    if fallback:
        return fallback
    raise PermissionDenied('No tienes acceso MedSupplier para esta organización.')


def filter_queryset_for_context(queryset, context):
    model = getattr(queryset, 'model', None)
    if not model:
        return queryset.none()

    queryset = queryset.filter(organization_id=context.organization_id)

    if context.is_customer:
        if model is models.MedSupplierAuditEvent:
            queryset = queryset.filter(account_id__in=context.account_ids, exportable=True)
        elif model is models.SupplierAccount:
            queryset = queryset.filter(id__in=context.account_ids)
        elif any(field.name == 'account' for field in model._meta.fields):
            queryset = queryset.filter(account_id__in=context.account_ids)
        elif any(field.name == 'document' for field in model._meta.fields):
            queryset = queryset.filter(document__account_id__in=context.account_ids)
        else:
            queryset = queryset.none()

    if model is not models.MedSupplierAuditEvent and any(field.name == 'visibility' for field in model._meta.fields):
        queryset = queryset.filter(visibility__in=context.visible_visibilities)

    return queryset


def assert_object_allowed(obj, context):
    account = getattr(obj, 'account', None)
    if account is None and hasattr(obj, 'document'):
        account = getattr(obj.document, 'account', None)
    if context.is_customer:
        if not account or not context.has_account_scope(account.id):
            raise PermissionDenied('Objeto fuera del account_scope permitido.')
        visibility = getattr(obj, 'visibility', 'customer_shared')
        if visibility not in CUSTOMER_VISIBLE_VISIBILITIES:
            raise PermissionDenied('Objeto no compartido con Customer.')
    return True


def assert_can_mutate(context):
    if not context.can_mutate or context.is_customer:
        raise PermissionDenied('No tienes permisos para modificar este registro MedSupplier.')
