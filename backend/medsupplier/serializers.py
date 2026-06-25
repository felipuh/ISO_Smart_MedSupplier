from rest_framework import serializers

from . import models


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

    class Meta:
        fields = ()
        read_only_fields = (
            'id', 'organization', 'created_by', 'updated_by', 'created_at', 'updated_at',
        )

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return ''

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return obj.updated_by.get_full_name() or obj.updated_by.email
        return ''


class SupplierAccountSerializer(BaseMedSupplierSerializer):
    class Meta:
        model = models.SupplierAccount
        fields = '__all__'
        read_only_fields = BaseMedSupplierSerializer.Meta.read_only_fields


class SupplierContactSerializer(BaseMedSupplierSerializer):
    related_fields = ('account',)

    class Meta:
        model = models.SupplierContact
        fields = '__all__'
        read_only_fields = BaseMedSupplierSerializer.Meta.read_only_fields


class SupplierMeetingSerializer(BaseMedSupplierSerializer):
    related_fields = ('account',)

    class Meta:
        model = models.SupplierMeeting
        fields = '__all__'
        read_only_fields = BaseMedSupplierSerializer.Meta.read_only_fields


class SupplierActionSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'meeting')

    class Meta:
        model = models.SupplierAction
        fields = '__all__'
        read_only_fields = BaseMedSupplierSerializer.Meta.read_only_fields


class SupplierRequirementSerializer(BaseMedSupplierSerializer):
    related_fields = ('account',)

    class Meta:
        model = models.SupplierRequirement
        fields = '__all__'
        read_only_fields = BaseMedSupplierSerializer.Meta.read_only_fields


class SupplierDocumentSerializer(BaseMedSupplierSerializer):
    related_fields = ('account',)

    class Meta:
        model = models.SupplierDocument
        fields = '__all__'
        read_only_fields = BaseMedSupplierSerializer.Meta.read_only_fields


class SupplierDocumentVersionSerializer(BaseMedSupplierSerializer):
    related_fields = ('document',)

    class Meta:
        model = models.SupplierDocumentVersion
        fields = '__all__'
        read_only_fields = BaseMedSupplierSerializer.Meta.read_only_fields


class SupplierRFQSerializer(BaseMedSupplierSerializer):
    related_fields = ('account',)

    class Meta:
        model = models.SupplierRFQ
        fields = '__all__'
        read_only_fields = BaseMedSupplierSerializer.Meta.read_only_fields

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


class SupplierQuoteSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'rfq')

    class Meta:
        model = models.SupplierQuote
        fields = '__all__'
        read_only_fields = BaseMedSupplierSerializer.Meta.read_only_fields


class SupplierPurchaseOrderSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'quote')

    class Meta:
        model = models.SupplierPurchaseOrder
        fields = '__all__'
        read_only_fields = BaseMedSupplierSerializer.Meta.read_only_fields


class SupplierLotSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'purchase_order')

    class Meta:
        model = models.SupplierLot
        fields = '__all__'
        read_only_fields = BaseMedSupplierSerializer.Meta.read_only_fields


class SupplierShipmentSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'purchase_order')

    class Meta:
        model = models.SupplierShipment
        fields = '__all__'
        read_only_fields = BaseMedSupplierSerializer.Meta.read_only_fields


class SupplierInspectionSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'shipment')

    class Meta:
        model = models.SupplierInspection
        fields = '__all__'
        read_only_fields = BaseMedSupplierSerializer.Meta.read_only_fields


class SupplierQualityEventSerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'inspection')

    class Meta:
        model = models.SupplierQualityEvent
        fields = '__all__'
        read_only_fields = BaseMedSupplierSerializer.Meta.read_only_fields


class SupplierCAPASerializer(BaseMedSupplierSerializer):
    related_fields = ('account', 'quality_event')

    class Meta:
        model = models.SupplierCAPA
        fields = '__all__'
        read_only_fields = BaseMedSupplierSerializer.Meta.read_only_fields


class SupplierScorecardSerializer(BaseMedSupplierSerializer):
    related_fields = ('account',)

    class Meta:
        model = models.SupplierScorecard
        fields = '__all__'
        read_only_fields = BaseMedSupplierSerializer.Meta.read_only_fields


class MedSupplierAuditEventSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = models.MedSupplierAuditEvent
        fields = '__all__'
        read_only_fields = fields

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return 'Sistema'
