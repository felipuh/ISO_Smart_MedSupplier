from django.contrib import admin

from . import models


@admin.register(models.SupplierAccount)
class SupplierAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_code', 'organization', 'status', 'risk_level', 'updated_at')
    search_fields = ('name', 'account_code', 'legal_name')
    list_filter = ('status', 'risk_level', 'regulated_industry')


admin.site.register(models.SupplierContact)
admin.site.register(models.SupplierMeeting)
admin.site.register(models.SupplierAction)
admin.site.register(models.SupplierRequirement)
admin.site.register(models.SupplierDocument)
admin.site.register(models.SupplierDocumentVersion)
admin.site.register(models.SupplierRFQ)
admin.site.register(models.SupplierQuote)
admin.site.register(models.SupplierPurchaseOrder)
admin.site.register(models.SupplierLot)
admin.site.register(models.SupplierShipment)
admin.site.register(models.SupplierInspection)
admin.site.register(models.SupplierQualityEvent)
admin.site.register(models.SupplierCAPA)
admin.site.register(models.SupplierScorecard)
admin.site.register(models.MedSupplierAuditEvent)
