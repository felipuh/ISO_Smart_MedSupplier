from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'accounts', views.SupplierAccountViewSet, basename='medsupplier-account')
router.register(r'contacts', views.SupplierContactViewSet, basename='medsupplier-contact')
router.register(r'meetings', views.SupplierMeetingViewSet, basename='medsupplier-meeting')
router.register(r'actions', views.SupplierActionViewSet, basename='medsupplier-action')
router.register(r'requirements', views.SupplierRequirementViewSet, basename='medsupplier-requirement')
router.register(r'documents', views.SupplierDocumentViewSet, basename='medsupplier-document')
router.register(r'document-versions', views.SupplierDocumentVersionViewSet, basename='medsupplier-document-version')
router.register(r'rfqs', views.SupplierRFQViewSet, basename='medsupplier-rfq')
router.register(r'quotes', views.SupplierQuoteViewSet, basename='medsupplier-quote')
router.register(r'quote-lines', views.SupplierQuoteLineViewSet, basename='medsupplier-quote-line')
router.register(r'purchase-orders', views.SupplierPurchaseOrderViewSet, basename='medsupplier-purchase-order')
router.register(r'order-lines', views.SupplierOrderLineViewSet, basename='medsupplier-order-line')
router.register(r'lots', views.SupplierLotViewSet, basename='medsupplier-lot')
router.register(r'shipments', views.SupplierShipmentViewSet, basename='medsupplier-shipment')
router.register(r'shipment-milestones', views.SupplierShipmentMilestoneViewSet, basename='medsupplier-shipment-milestone')
router.register(r'inspections', views.SupplierInspectionViewSet, basename='medsupplier-inspection')
router.register(r'quality-events', views.SupplierQualityEventViewSet, basename='medsupplier-quality-event')
router.register(r'capas', views.SupplierCAPAViewSet, basename='medsupplier-capa')
router.register(r'fmeas', views.SupplierFMEAViewSet, basename='medsupplier-fmea')
router.register(r'fmea-items', views.SupplierFMEAItemViewSet, basename='medsupplier-fmea-item')
router.register(r'scorecards', views.SupplierScorecardViewSet, basename='medsupplier-scorecard')
router.register(r'audit-events', views.MedSupplierAuditEventViewSet, basename='medsupplier-audit-event')
router.register(r'esignatures', views.MedSupplierESignatureViewSet, basename='medsupplier-esignature')
router.register(r'evidence-packages', views.EvidencePackageViewSet, basename='medsupplier-evidence-package')
router.register(r'evidence-package-entries', views.EvidencePackageEntryViewSet, basename='medsupplier-evidence-package-entry')

urlpatterns = [
    path('me/permissions/', views.effective_permissions, name='medsupplier-effective-permissions'),
    path('dashboard/summary/', views.dashboard_summary, name='medsupplier-dashboard-summary'),
    path('cockpit/private/', views.private_cockpit, name='medsupplier-private-cockpit'),
    path('integration/status/', views.integration_status, name='medsupplier-integration-status'),
    path('', include(router.urls)),
]
