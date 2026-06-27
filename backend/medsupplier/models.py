from django.conf import settings
from django.db import models
from django.utils import timezone
import hashlib
import json
import uuid


class OrganizationStampedModel(models.Model):
    """Base tenant-scoped model for regulated Supplier-Customer records."""

    VISIBILITY_CHOICES = [
        ('public_shared', 'Compartido público controlado'),
        ('customer_shared', 'Compartido con cliente'),
        ('supplier_private', 'Privado Supplier'),
        ('supplier_confidential', 'Confidencial Supplier'),
        ('regulated_evidence', 'Evidencia regulada'),
        ('audit_only', 'Solo auditoría'),
        ('archived', 'Archivado'),
        ('obsolete', 'Obsoleto'),
        ('shared', 'Legacy compartido'),
        ('private', 'Legacy privado'),
    ]

    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='%(class)ss')
    visibility = models.CharField(max_length=30, choices=VISIBILITY_CHOICES, default='shared')
    metadata = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MedSupplierUserScope(models.Model):
    SIDE_CHOICES = [
        ('supplier', 'Supplier'),
        ('customer', 'Customer'),
    ]
    ROLE_CHOICES = [
        ('supplier_admin', 'Supplier Admin'),
        ('supplier_sales', 'Supplier Sales'),
        ('supplier_finance', 'Supplier Finance'),
        ('supplier_quality', 'Supplier Quality'),
        ('supplier_logistics', 'Supplier Logistics'),
        ('supplier_viewer', 'Supplier Viewer'),
        ('customer_admin', 'Customer Admin'),
        ('customer_buyer', 'Customer Buyer / Procurement'),
        ('customer_quality', 'Customer Quality'),
        ('customer_logistics', 'Customer Logistics'),
        ('customer_auditor', 'Customer Auditor'),
        ('customer_viewer', 'Customer Viewer'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medsupplier_scopes')
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='medsupplier_user_scopes')
    account = models.ForeignKey('SupplierAccount', on_delete=models.CASCADE, null=True, blank=True, related_name='user_scopes')
    side = models.CharField(max_length=20, choices=SIDE_CHOICES)
    role = models.CharField(max_length=40, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medsupplier_user_scopes'
        ordering = ['organization', 'side', 'role']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'organization', 'account', 'role'],
                name='uniq_medsupplier_user_scope',
            )
        ]
        indexes = [
            models.Index(fields=['organization', 'side', 'role']),
            models.Index(fields=['user', 'organization', 'is_active']),
        ]

    def __str__(self):
        account = self.account.account_code if self.account else 'all-accounts'
        return f'{self.user_id} {self.role} {account}'


class SupplierAccount(OrganizationStampedModel):
    STATUS_CHOICES = [
        ('prospect', 'Prospecto'),
        ('active', 'Activo'),
        ('on_hold', 'En espera'),
        ('disqualified', 'Descalificado'),
        ('inactive', 'Inactivo'),
    ]
    RISK_CHOICES = [
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
        ('critical', 'Crítico'),
    ]

    name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255, blank=True)
    account_code = models.CharField(max_length=60)
    regulated_industry = models.BooleanField(default=True)
    customer_segment = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=100, blank=True)
    primary_contact_email = models.EmailField(blank=True)
    account_owner = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='active')
    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES, default='medium')
    next_qbr_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'medsupplier_accounts'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'account_code'], name='uniq_medsupplier_account_code')
        ]
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'risk_level']),
        ]

    def __str__(self):
        return f'{self.account_code} - {self.name}'


class SupplierContact(OrganizationStampedModel):
    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='contacts')
    full_name = models.CharField(max_length=180)
    email = models.EmailField(blank=True)
    role_title = models.CharField(max_length=150, blank=True)
    department = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    is_customer_user = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'medsupplier_contacts'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class SupplierMeeting(OrganizationStampedModel):
    STATUS_CHOICES = [
        ('planned', 'Planificada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]

    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='meetings')
    title = models.CharField(max_length=255)
    meeting_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    agenda = models.TextField(blank=True)
    minutes = models.TextField(blank=True)
    attendees = models.JSONField(default=list, blank=True)
    decisions = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'medsupplier_meetings'
        ordering = ['-meeting_date']

    def __str__(self):
        return self.title


class SupplierAction(OrganizationStampedModel):
    STATUS_CHOICES = [
        ('open', 'Abierta'),
        ('in_progress', 'En progreso'),
        ('blocked', 'Bloqueada'),
        ('closed', 'Cerrada'),
    ]

    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='actions')
    meeting = models.ForeignKey(SupplierMeeting, on_delete=models.SET_NULL, null=True, blank=True, related_name='actions')
    title = models.CharField(max_length=255)
    owner = models.CharField(max_length=150, blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'medsupplier_actions'
        ordering = ['status', 'due_date']

    def __str__(self):
        return self.title


class SupplierRequirement(OrganizationStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('under_review', 'En revisión'),
        ('approved', 'Aprobado'),
        ('superseded', 'Reemplazado'),
        ('obsolete', 'Obsoleto'),
    ]

    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='requirements')
    requirement_id = models.CharField(max_length=80)
    title = models.CharField(max_length=255)
    requirement_type = models.CharField(max_length=80, default='customer')
    source_reference = models.CharField(max_length=180, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')
    effective_date = models.DateField(null=True, blank=True)
    owner = models.CharField(max_length=150, blank=True)

    class Meta:
        db_table = 'medsupplier_requirements'
        ordering = ['requirement_id']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'requirement_id'], name='uniq_medsupplier_requirement_id')
        ]

    def __str__(self):
        return f'{self.requirement_id} - {self.title}'


class SupplierDocument(OrganizationStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('under_review', 'En revisión'),
        ('effective', 'Vigente'),
        ('obsolete', 'Obsoleto'),
    ]

    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    document_number = models.CharField(max_length=100)
    document_type = models.CharField(max_length=80)
    current_revision = models.CharField(max_length=30, default='A')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')
    confidentiality = models.CharField(max_length=50, default='controlled')
    owner = models.CharField(max_length=150, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    obsolete_date = models.DateField(null=True, blank=True)
    next_review_date = models.DateField(null=True, blank=True)
    major_version = models.PositiveIntegerField(default=1)
    minor_version = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'medsupplier_documents'
        ordering = ['document_number']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'document_number'], name='uniq_medsupplier_document_number')
        ]

    def __str__(self):
        return f'{self.document_number} rev {self.current_revision}'


class SupplierDocumentVersion(OrganizationStampedModel):
    document = models.ForeignKey(SupplierDocument, on_delete=models.CASCADE, related_name='versions')
    revision = models.CharField(max_length=30)
    change_reason = models.TextField()
    file = models.FileField(upload_to='medsupplier/documents/', blank=True, null=True)
    checksum = models.CharField(max_length=128, blank=True)
    approved_by = models.CharField(max_length=150, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'medsupplier_document_versions'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['document', 'revision'], name='uniq_medsupplier_document_revision')
        ]

    def __str__(self):
        return f'{self.document.document_number} rev {self.revision}'


class SupplierRFQ(OrganizationStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('sent', 'Enviada'),
        ('quoted', 'Cotizada'),
        ('closed', 'Cerrada'),
        ('cancelled', 'Cancelada'),
    ]

    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='rfqs')
    rfq_number = models.CharField(max_length=80)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')
    requested_due_date = models.DateField(null=True, blank=True)
    requirements = models.ManyToManyField(SupplierRequirement, blank=True, related_name='rfqs')
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'medsupplier_rfqs'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'rfq_number'], name='uniq_medsupplier_rfq_number')
        ]

    def __str__(self):
        return self.rfq_number


class SupplierQuote(OrganizationStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('submitted', 'Presentada'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
        ('expired', 'Expirada'),
    ]

    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='quotes')
    rfq = models.ForeignKey(SupplierRFQ, on_delete=models.SET_NULL, null=True, blank=True, related_name='quotes')
    quote_number = models.CharField(max_length=80)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')
    currency = models.CharField(max_length=3, default='USD')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    valid_until = models.DateField(null=True, blank=True)
    private_margin_notes = models.TextField(blank=True)
    supplier_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    margin = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    commission = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    advance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    internal_notes = models.TextField(blank=True)
    forecast_probability = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'medsupplier_quotes'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'quote_number'], name='uniq_medsupplier_quote_number')
        ]

    def __str__(self):
        return self.quote_number


class SupplierQuoteLine(OrganizationStampedModel):
    quote = models.ForeignKey(SupplierQuote, on_delete=models.CASCADE, related_name='lines')
    rfq = models.ForeignKey(SupplierRFQ, on_delete=models.SET_NULL, null=True, blank=True, related_name='quote_lines')
    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='quote_lines')
    line_number = models.PositiveIntegerField(default=1)
    product_code = models.CharField(max_length=120, blank=True)
    description = models.TextField()
    technical_description = models.TextField(blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    uom = models.CharField(max_length=30, default='EA')
    moq = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    lead_time_days = models.PositiveIntegerField(default=0)
    tooling = models.CharField(max_length=180, blank=True)
    incoterm = models.CharField(max_length=30, blank=True)
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    supplier_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    margin = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    valid_until = models.DateField(null=True, blank=True)
    taxes_and_charges = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    customer_notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    class Meta:
        db_table = 'medsupplier_quote_lines'
        ordering = ['quote', 'line_number']
        constraints = [
            models.UniqueConstraint(fields=['quote', 'line_number'], name='uniq_medsupplier_quote_line')
        ]

    def __str__(self):
        return f'{self.quote.quote_number}-{self.line_number}'


class SupplierPurchaseOrder(OrganizationStampedModel):
    STATUS_CHOICES = [
        ('received', 'Recibida'),
        ('confirmed', 'Confirmada'),
        ('in_production', 'En producción'),
        ('shipped', 'Enviada'),
        ('closed', 'Cerrada'),
        ('cancelled', 'Cancelada'),
    ]

    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='purchase_orders')
    quote = models.ForeignKey(SupplierQuote, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_orders')
    po_number = models.CharField(max_length=100)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='received')
    customer_po_date = models.DateField(null=True, blank=True)
    promised_ship_date = models.DateField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        db_table = 'medsupplier_purchase_orders'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'po_number'], name='uniq_medsupplier_po_number')
        ]

    def __str__(self):
        return self.po_number


class SupplierOrderLine(OrganizationStampedModel):
    STATUS_CHOICES = [
        ('open', 'Abierta'),
        ('confirmed', 'Confirmada'),
        ('partial', 'Parcial'),
        ('delivered', 'Entregada'),
        ('closed', 'Cerrada'),
        ('cancelled', 'Cancelada'),
    ]

    purchase_order = models.ForeignKey(SupplierPurchaseOrder, on_delete=models.CASCADE, related_name='lines')
    quote_line = models.ForeignKey(SupplierQuoteLine, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_lines')
    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='order_lines')
    line_number = models.PositiveIntegerField(default=1)
    product_code = models.CharField(max_length=120, blank=True)
    description = models.TextField()
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    delivered_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    pending_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    uom = models.CharField(max_length=30, default='EA')
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='open')
    discrepancy_notes = models.TextField(blank=True)

    class Meta:
        db_table = 'medsupplier_order_lines'
        ordering = ['purchase_order', 'line_number']
        constraints = [
            models.UniqueConstraint(fields=['purchase_order', 'line_number'], name='uniq_medsupplier_order_line')
        ]

    def __str__(self):
        return f'{self.purchase_order.po_number}-{self.line_number}'


class SupplierLot(OrganizationStampedModel):
    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='lots')
    purchase_order = models.ForeignKey(SupplierPurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='lots')
    lot_number = models.CharField(max_length=100)
    product_code = models.CharField(max_length=120)
    product_description = models.CharField(max_length=255, blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    uom = models.CharField(max_length=30, default='EA')
    manufactured_at = models.DateField(null=True, blank=True)
    expiration_at = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'medsupplier_lots'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'lot_number'], name='uniq_medsupplier_lot_number')
        ]

    def __str__(self):
        return self.lot_number


class SupplierShipment(OrganizationStampedModel):
    STATUS_CHOICES = [
        ('planned', 'Planificado'),
        ('in_transit', 'En tránsito'),
        ('delivered', 'Entregado'),
        ('delayed', 'Retrasado'),
        ('cancelled', 'Cancelado'),
    ]

    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='shipments')
    purchase_order = models.ForeignKey(SupplierPurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipments')
    shipment_number = models.CharField(max_length=100)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='planned')
    carrier = models.CharField(max_length=120, blank=True)
    tracking_number = models.CharField(max_length=120, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    asn_number = models.CharField(max_length=120, blank=True)
    pod_reference = models.CharField(max_length=120, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    delay_reason = models.TextField(blank=True)
    is_partial = models.BooleanField(default=False)

    class Meta:
        db_table = 'medsupplier_shipments'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'shipment_number'], name='uniq_medsupplier_shipment_number')
        ]

    def __str__(self):
        return self.shipment_number


class SupplierShipmentMilestone(OrganizationStampedModel):
    STATUS_CHOICES = [
        ('planned', 'Planificado'),
        ('completed', 'Completado'),
        ('delayed', 'Retrasado'),
        ('cancelled', 'Cancelado'),
    ]

    shipment = models.ForeignKey(SupplierShipment, on_delete=models.CASCADE, related_name='milestones')
    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='shipment_milestones')
    milestone_type = models.CharField(max_length=80)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='planned')
    expected_at = models.DateTimeField(null=True, blank=True)
    actual_at = models.DateTimeField(null=True, blank=True)
    carrier = models.CharField(max_length=120, blank=True)
    tracking_number = models.CharField(max_length=120, blank=True)
    incident_notes = models.TextField(blank=True)
    delay_reason = models.TextField(blank=True)

    class Meta:
        db_table = 'medsupplier_shipment_milestones'
        ordering = ['shipment', 'expected_at', 'created_at']

    def __str__(self):
        return f'{self.shipment.shipment_number} {self.milestone_type}'


class SupplierInspection(OrganizationStampedModel):
    RESULT_CHOICES = [
        ('pending', 'Pendiente'),
        ('accepted', 'Aceptado'),
        ('accepted_with_deviation', 'Aceptado con desviación'),
        ('rejected', 'Rechazado'),
    ]

    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='inspections')
    shipment = models.ForeignKey(SupplierShipment, on_delete=models.SET_NULL, null=True, blank=True, related_name='inspections')
    inspection_number = models.CharField(max_length=100)
    received_at = models.DateTimeField(null=True, blank=True)
    result = models.CharField(max_length=40, choices=RESULT_CHOICES, default='pending')
    inspected_by = models.CharField(max_length=150, blank=True)
    findings = models.TextField(blank=True)

    class Meta:
        db_table = 'medsupplier_inspections'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'inspection_number'], name='uniq_medsupplier_inspection_number')
        ]

    def __str__(self):
        return self.inspection_number


class SupplierQualityEvent(OrganizationStampedModel):
    EVENT_CHOICES = [
        ('ncr', 'NCR'),
        ('complaint', 'Queja'),
        ('deviation', 'Desviación'),
        ('audit_finding', 'Hallazgo de auditoría'),
    ]
    STATUS_CHOICES = [
        ('open', 'Abierto'),
        ('triage', 'Triage'),
        ('investigation', 'Investigación'),
        ('capa_required', 'CAPA requerida'),
        ('closed', 'Cerrado'),
    ]

    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='quality_events')
    inspection = models.ForeignKey(SupplierInspection, on_delete=models.SET_NULL, null=True, blank=True, related_name='quality_events')
    event_number = models.CharField(max_length=100)
    event_type = models.CharField(max_length=40, choices=EVENT_CHOICES)
    severity = models.CharField(max_length=20, default='medium')
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='open')
    title = models.CharField(max_length=255)
    description = models.TextField()
    reported_at = models.DateTimeField(default=timezone.now)
    owner = models.CharField(max_length=150, blank=True)

    class Meta:
        db_table = 'medsupplier_quality_events'
        ordering = ['-reported_at']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'event_number'], name='uniq_medsupplier_quality_event_number')
        ]

    def __str__(self):
        return self.event_number


class SupplierCAPA(OrganizationStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('open', 'Abierta'),
        ('effectiveness_check', 'Verificación de efectividad'),
        ('closed', 'Cerrada'),
        ('cancelled', 'Cancelada'),
    ]

    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='capas')
    quality_event = models.ForeignKey(SupplierQualityEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name='capas')
    capa_number = models.CharField(max_length=100)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='draft')
    root_cause = models.TextField(blank=True)
    corrective_action = models.TextField(blank=True)
    preventive_action = models.TextField(blank=True)
    owner = models.CharField(max_length=150, blank=True)
    due_date = models.DateField(null=True, blank=True)
    effectiveness_result = models.TextField(blank=True)
    evidence_summary = models.TextField(blank=True)

    class Meta:
        db_table = 'medsupplier_capas'
        ordering = ['status', 'due_date']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'capa_number'], name='uniq_medsupplier_capa_number')
        ]

    def __str__(self):
        return self.capa_number


class SupplierFMEA(OrganizationStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('under_review', 'En revisión'),
        ('closed', 'Cerrado'),
        ('obsolete', 'Obsoleto'),
    ]

    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='fmeas')
    fmea_number = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    process = models.CharField(max_length=180, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')
    owner = models.CharField(max_length=150, blank=True)
    review_due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'medsupplier_fmeas'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'fmea_number'], name='uniq_medsupplier_fmea_number')
        ]

    def __str__(self):
        return self.fmea_number


class SupplierFMEAItem(OrganizationStampedModel):
    STATUS_CHOICES = [
        ('open', 'Abierto'),
        ('mitigating', 'En mitigación'),
        ('accepted', 'Aceptado'),
        ('closed', 'Cerrado'),
    ]

    fmea = models.ForeignKey(SupplierFMEA, on_delete=models.CASCADE, related_name='items')
    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='fmea_items')
    quality_event = models.ForeignKey(SupplierQualityEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name='fmea_items')
    capa = models.ForeignKey(SupplierCAPA, on_delete=models.SET_NULL, null=True, blank=True, related_name='fmea_items')
    document = models.ForeignKey(SupplierDocument, on_delete=models.SET_NULL, null=True, blank=True, related_name='fmea_items')
    hazard = models.CharField(max_length=255)
    failure_mode = models.CharField(max_length=255)
    cause = models.TextField(blank=True)
    effect = models.TextField(blank=True)
    severity = models.PositiveSmallIntegerField(default=1)
    occurrence = models.PositiveSmallIntegerField(default=1)
    detection = models.PositiveSmallIntegerField(default=1)
    risk_score = models.PositiveIntegerField(default=1)
    mitigation = models.TextField(blank=True)
    owner = models.CharField(max_length=150, blank=True)
    due_date = models.DateField(null=True, blank=True)
    residual_risk = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='open')

    class Meta:
        db_table = 'medsupplier_fmea_items'
        ordering = ['-risk_score', 'due_date']

    def save(self, *args, **kwargs):
        self.risk_score = int(self.severity or 0) * int(self.occurrence or 0) * int(self.detection or 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.fmea.fmea_number} {self.failure_mode}'


class SupplierScorecard(OrganizationStampedModel):
    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='scorecards')
    period_start = models.DateField()
    period_end = models.DateField()
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    delivery_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    responsiveness_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    qbr_notes = models.TextField(blank=True)

    class Meta:
        db_table = 'medsupplier_scorecards'
        ordering = ['-period_end']
        constraints = [
            models.UniqueConstraint(fields=['account', 'period_start', 'period_end'], name='uniq_medsupplier_scorecard_period')
        ]

    def __str__(self):
        return f'{self.account.name} {self.period_start} - {self.period_end}'


class MedSupplierAuditEvent(models.Model):
    ACTION_CHOICES = [
        ('create', 'Creación'),
        ('update', 'Actualización'),
        ('delete', 'Eliminación'),
        ('export', 'Exportación'),
        ('status_change', 'Cambio de estado'),
    ]

    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='medsupplier_audit_events')
    account = models.ForeignKey(SupplierAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_events')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    correlation_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    record_type = models.CharField(max_length=80)
    record_id = models.CharField(max_length=80)
    object_type = models.CharField(max_length=120, blank=True)
    object_id = models.CharField(max_length=120, blank=True)
    description = models.TextField()
    reason = models.TextField(blank=True)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    exportable = models.BooleanField(default=True)
    previous_hash = models.CharField(max_length=64, blank=True)
    event_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'medsupplier_audit_events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['record_type', 'record_id']),
            models.Index(fields=['organization', 'account', '-created_at']),
        ]

    def calculate_hash(self):
        payload = {
            'organization_id': self.organization_id,
            'account_id': self.account_id,
            'user_id': self.user_id,
            'correlation_id': str(self.correlation_id),
            'action': self.action,
            'record_type': self.record_type,
            'record_id': self.record_id,
            'object_type': self.object_type,
            'object_id': self.object_id,
            'description': self.description,
            'reason': self.reason,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'previous_hash': self.previous_hash,
            'created_at': self.created_at.isoformat() if self.created_at else '',
        }
        serialized = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        if not self.object_type:
            self.object_type = self.record_type
        if not self.object_id:
            self.object_id = self.record_id
        if not self.previous_hash:
            previous = MedSupplierAuditEvent.objects.filter(
                organization_id=self.organization_id,
            ).exclude(pk=self.pk).order_by('-created_at', '-id').first()
            self.previous_hash = previous.event_hash if previous else ''
        super().save(*args, **kwargs)
        if not self.event_hash:
            self.event_hash = self.calculate_hash()
            super().save(update_fields=['event_hash'])

    def __str__(self):
        return f'{self.action} {self.record_type}:{self.record_id}'


class MedSupplierESignature(models.Model):
    MEANING_CHOICES = [
        ('approval', 'Aprobación'),
        ('review', 'Revisión'),
        ('closure', 'Cierre'),
        ('status_change', 'Cambio de estado'),
        ('export_approval', 'Aprobación de exportación'),
    ]

    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='medsupplier_esignatures')
    account = models.ForeignKey(SupplierAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='esignatures')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='medsupplier_esignatures')
    meaning = models.CharField(max_length=40, choices=MEANING_CHOICES)
    reason = models.TextField()
    object_type = models.CharField(max_length=120)
    object_id = models.CharField(max_length=120)
    correlation_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    signature_hash = models.CharField(max_length=64, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    signed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'medsupplier_esignatures'
        ordering = ['-signed_at']
        indexes = [
            models.Index(fields=['organization', 'object_type', 'object_id']),
            models.Index(fields=['user', '-signed_at']),
        ]

    def calculate_hash(self):
        payload = {
            'organization_id': self.organization_id,
            'account_id': self.account_id,
            'user_id': self.user_id,
            'meaning': self.meaning,
            'reason': self.reason,
            'object_type': self.object_type,
            'object_id': self.object_id,
            'correlation_id': str(self.correlation_id),
            'signed_at': self.signed_at.isoformat() if self.signed_at else '',
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.signature_hash:
            self.signature_hash = self.calculate_hash()
            super().save(update_fields=['signature_hash'])

    def __str__(self):
        return f'{self.meaning} {self.object_type}:{self.object_id}'


class EvidencePackage(OrganizationStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('prepared', 'Preparado'),
        ('approved', 'Aprobado'),
        ('exported', 'Exportado'),
        ('archived', 'Archivado'),
    ]

    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='evidence_packages')
    package_number = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    scope = models.CharField(max_length=120, blank=True)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    version = models.CharField(max_length=30, default='1.0')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_evidence_packages')
    generated_at = models.DateTimeField(null=True, blank=True)
    checksum = models.CharField(max_length=64, blank=True)
    export_format = models.CharField(max_length=20, default='json')
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'medsupplier_evidence_packages'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'package_number'], name='uniq_medsupplier_evidence_package')
        ]

    def calculate_checksum(self):
        payload = {
            'organization_id': self.organization_id,
            'account_id': self.account_id,
            'package_number': self.package_number,
            'title': self.title,
            'version': self.version,
            'status': self.status,
            'entries': list(self.entries.values('object_type', 'object_id', 'label').order_by('object_type', 'object_id')),
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode('utf-8')).hexdigest()

    def __str__(self):
        return self.package_number


class EvidencePackageEntry(models.Model):
    package = models.ForeignKey(EvidencePackage, on_delete=models.CASCADE, related_name='entries')
    object_type = models.CharField(max_length=120)
    object_id = models.CharField(max_length=120)
    label = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'medsupplier_evidence_package_entries'
        ordering = ['object_type', 'object_id']
        constraints = [
            models.UniqueConstraint(fields=['package', 'object_type', 'object_id'], name='uniq_medsupplier_evidence_entry')
        ]

    def __str__(self):
        return f'{self.package.package_number} {self.object_type}:{self.object_id}'
