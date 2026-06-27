from rest_framework import serializers

from . import models


PRIVATE_COMMERCIAL_FIELDS = {
    'private_margin_notes',
    'supplier_cost',
    'margin',
    'commission',
    'advance',
    'internal_notes',
    'pricing_internal',
    'forecast_probability',
    'private_notes',
    'supplier_private_notes',
    'internal_cost',
    'internal_price',
    'forecast_private',
}

BASE_FIELDS = [
    'id', 'organization', 'visibility', 'metadata', 'created_by', 'updated_by',
    'created_at', 'updated_at', 'created_by_name', 'updated_by_name',
]
BASE_READ_ONLY_FIELDS = [
    'id', 'organization', 'created_by', 'updated_by', 'created_at', 'updated_at',
    'created_by_name', 'updated_by_name',
]


class OrganizationRelationValidator:
    related_fields = ()

    def validate(self, attrs):
        request = self.context.get('request')
        organization_id = getattr(request, 'organization_id', None)
        if organization_id in (None, ''):
            organization_id = request.query_params.get('organization_id') if request else None
        organization_id = int(organization_id) if organization_id else None

        for field_name in self.related_fields:
            related = attrs.get(field_name) or getattr(self.instance, field_name, None)
            if related and organization_id and related.organization_id != organization_id:
                raise serializers.ValidationError({
                    field_name: 'El registro relacionado pertenece a otra organización.'
                })
        return attrs


class BaseMedSupplierSerializer(OrganizationRelationValidator, serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    def get_fields(self):
        fields = super().get_fields()
        medsupplier_context = self.context.get('medsupplier_context')
        if medsupplier_context and medsupplier_context.is_customer:
            for field_name in PRIVATE_COMMERCIAL_FIELDS:
                fields.pop(field_name, None)
        elif medsupplier_context and not medsupplier_context.can_view_private_financials:
            for field_name in {'supplier_cost', 'margin', 'commission', 'advance'}:
                fields.pop(field_name, None)
        return fields

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return ''

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return obj.updated_by.get_full_name() or obj.updated_by.email
        return ''


class MedSupplierUserScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MedSupplierUserScope
        fields = [
            'id', 'user', 'organization', 'account', 'side', 'role', 'is_active',
            'metadata', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SupplierAccountSerializer(BaseMedSupplierSerializer):
    class Meta:
        model = models.SupplierAccount
        fields = BASE_FIELDS + [
            'name', 'legal_name', 'account_code', 'regulated_industry',
            'customer_segment', 'country', 'primary_contact_email',
            'account_owner', 'status', 'risk_level', 'next_qbr_date',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierContactSerializer(BaseMedSupplierSerializer):
    related_fields = ('account',)

    class Meta:
        model = models.SupplierContact
        fields = BASE_FIELDS + [
            'account', 'full_name', 'email', 'role_title', 'department',
            'phone', 'is_customer_user', 'is_active',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierMeetingSerializer(BaseMedSupplierSerializer):
    related_fields = ('account',)

    class Meta:
        model = models.SupplierMeeting
        fields = BASE_FIELDS + [
            'account', 'title', 'meeting_date', 'status', 'agenda', 'minutes',
            'attendees', 'decisions',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierActionSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'meeting')

    class Meta:
        model = models.SupplierAction
        fields = BASE_FIELDS + [
            'account', 'meeting', 'title', 'owner', 'due_date', 'status',
            'description',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierRequirementSerializer(BaseMedSupplierSerializer):
    related_fields = ('account',)

    class Meta:
        model = models.SupplierRequirement
        fields = BASE_FIELDS + [
            'account', 'requirement_id', 'title', 'requirement_type',
            'source_reference', 'description', 'status', 'effective_date',
            'owner',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierDocumentSerializer(BaseMedSupplierSerializer):
    related_fields = ('account',)

    class Meta:
        model = models.SupplierDocument
        fields = BASE_FIELDS + [
            'account', 'title', 'document_number', 'document_type',
            'current_revision', 'status', 'confidentiality', 'owner',
            'effective_date', 'obsolete_date', 'next_review_date',
            'major_version', 'minor_version',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierDocumentVersionSerializer(BaseMedSupplierSerializer):
    related_fields = ('document',)

    class Meta:
        model = models.SupplierDocumentVersion
        fields = BASE_FIELDS + [
            'document', 'revision', 'change_reason', 'file', 'checksum',
            'approved_by', 'approved_at',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierRFQSerializer(BaseMedSupplierSerializer):
    related_fields = ('account',)

    class Meta:
        model = models.SupplierRFQ
        fields = BASE_FIELDS + [
            'account', 'rfq_number', 'title', 'status', 'requested_due_date',
            'requirements', 'notes',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context.get('request')
        organization_id = getattr(request, 'organization_id', None) or request.query_params.get('organization_id')
        if organization_id:
            for requirement in attrs.get('requirements', []):
                if requirement.organization_id != int(organization_id):
                    raise serializers.ValidationError({
                        'requirements': 'Todos los requisitos deben pertenecer a la organización activa.'
                    })
        return attrs


class SupplierQuoteLineSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'quote', 'rfq')

    class Meta:
        model = models.SupplierQuoteLine
        fields = BASE_FIELDS + [
            'quote', 'rfq', 'account', 'line_number', 'product_code',
            'description', 'technical_description', 'quantity', 'uom', 'moq',
            'lead_time_days', 'tooling', 'incoterm', 'unit_price',
            'supplier_cost', 'margin', 'currency', 'valid_until',
            'taxes_and_charges', 'customer_notes', 'internal_notes',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierQuoteSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'rfq')
    lines = SupplierQuoteLineSerializer(many=True, read_only=True)

    class Meta:
        model = models.SupplierQuote
        fields = BASE_FIELDS + [
            'account', 'rfq', 'quote_number', 'status', 'currency',
            'total_amount', 'valid_until', 'private_margin_notes',
            'supplier_cost', 'margin', 'commission', 'advance',
            'internal_notes', 'forecast_probability', 'lines',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierOrderLineSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'purchase_order', 'quote_line')

    class Meta:
        model = models.SupplierOrderLine
        fields = BASE_FIELDS + [
            'purchase_order', 'quote_line', 'account', 'line_number',
            'product_code', 'description', 'quantity', 'delivered_quantity',
            'pending_quantity', 'uom', 'due_date', 'status',
            'discrepancy_notes',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierPurchaseOrderSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'quote')
    lines = SupplierOrderLineSerializer(many=True, read_only=True)

    class Meta:
        model = models.SupplierPurchaseOrder
        fields = BASE_FIELDS + [
            'account', 'quote', 'po_number', 'status', 'customer_po_date',
            'promised_ship_date', 'currency', 'total_amount', 'lines',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierLotSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'purchase_order')

    class Meta:
        model = models.SupplierLot
        fields = BASE_FIELDS + [
            'account', 'purchase_order', 'lot_number', 'product_code',
            'product_description', 'quantity', 'uom', 'manufactured_at',
            'expiration_at',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierShipmentMilestoneSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'shipment')

    class Meta:
        model = models.SupplierShipmentMilestone
        fields = BASE_FIELDS + [
            'shipment', 'account', 'milestone_type', 'status', 'expected_at',
            'actual_at', 'carrier', 'tracking_number', 'incident_notes',
            'delay_reason',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierShipmentSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'purchase_order')
    milestones = SupplierShipmentMilestoneSerializer(many=True, read_only=True)

    class Meta:
        model = models.SupplierShipment
        fields = BASE_FIELDS + [
            'account', 'purchase_order', 'shipment_number', 'status',
            'carrier', 'tracking_number', 'shipped_at', 'delivered_at',
            'asn_number', 'pod_reference', 'expected_delivery_date',
            'delay_reason', 'is_partial', 'milestones',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierInspectionSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'shipment')

    class Meta:
        model = models.SupplierInspection
        fields = BASE_FIELDS + [
            'account', 'shipment', 'inspection_number', 'received_at',
            'result', 'inspected_by', 'findings',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierQualityEventSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'inspection')

    class Meta:
        model = models.SupplierQualityEvent
        fields = BASE_FIELDS + [
            'account', 'inspection', 'event_number', 'event_type', 'severity',
            'status', 'title', 'description', 'reported_at', 'owner',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierCAPASerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'quality_event')

    class Meta:
        model = models.SupplierCAPA
        fields = BASE_FIELDS + [
            'account', 'quality_event', 'capa_number', 'status', 'root_cause',
            'corrective_action', 'preventive_action', 'owner', 'due_date',
            'effectiveness_result', 'evidence_summary',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierFMEASerializer(BaseMedSupplierSerializer):
    related_fields = ('account',)

    class Meta:
        model = models.SupplierFMEA
        fields = BASE_FIELDS + [
            'account', 'fmea_number', 'title', 'process', 'status', 'owner',
            'review_due_date', 'notes',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class SupplierFMEAItemSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'fmea', 'quality_event', 'capa', 'document')

    class Meta:
        model = models.SupplierFMEAItem
        fields = BASE_FIELDS + [
            'fmea', 'account', 'quality_event', 'capa', 'document', 'hazard',
            'failure_mode', 'cause', 'effect', 'severity', 'occurrence',
            'detection', 'risk_score', 'mitigation', 'owner', 'due_date',
            'residual_risk', 'status',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS + ['risk_score']


class SupplierScorecardSerializer(BaseMedSupplierSerializer):
    related_fields = ('account',)

    class Meta:
        model = models.SupplierScorecard
        fields = BASE_FIELDS + [
            'account', 'period_start', 'period_end', 'quality_score',
            'delivery_score', 'responsiveness_score', 'overall_score',
            'qbr_notes',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS


class MedSupplierESignatureSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = models.MedSupplierESignature
        fields = [
            'id', 'organization', 'account', 'user', 'user_name', 'meaning',
            'reason', 'object_type', 'object_id', 'correlation_id',
            'signature_hash', 'ip_address', 'user_agent', 'signed_at',
        ]
        read_only_fields = fields

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email


class EvidencePackageEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EvidencePackageEntry
        fields = ['id', 'package', 'object_type', 'object_id', 'label', 'metadata', 'added_at']
        read_only_fields = ['id', 'added_at']


class EvidencePackageSerializer(BaseMedSupplierSerializer):
    related_fields = ('account',)
    entries = EvidencePackageEntrySerializer(many=True, read_only=True)

    class Meta:
        model = models.EvidencePackage
        fields = BASE_FIELDS + [
            'account', 'package_number', 'title', 'scope', 'date_from',
            'date_to', 'version', 'status', 'generated_by', 'generated_at',
            'checksum', 'export_format', 'entries',
        ]
        read_only_fields = BASE_READ_ONLY_FIELDS + ['generated_by', 'generated_at', 'checksum']


class MedSupplierAuditEventSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = models.MedSupplierAuditEvent
        fields = [
            'id', 'organization', 'account', 'user', 'user_name',
            'correlation_id', 'action', 'record_type', 'record_id',
            'object_type', 'object_id', 'description', 'reason', 'old_values',
            'new_values', 'ip_address', 'user_agent', 'exportable',
            'previous_hash', 'event_hash', 'created_at',
        ]
        read_only_fields = fields

    def get_fields(self):
        fields = super().get_fields()
        medsupplier_context = self.context.get('medsupplier_context')
        if medsupplier_context and medsupplier_context.is_customer:
            fields.pop('old_values', None)
            fields.pop('new_values', None)
            fields.pop('ip_address', None)
            fields.pop('user_agent', None)
        return fields

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return 'Sistema'
