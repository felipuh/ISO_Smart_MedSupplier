# Traceability Matrix

Date: 2026-06-29

This matrix maps MedSupplier requirements to implementation and current automated evidence. It is validation-ready and audit-ready, but requires formal customer/company validation before regulated production use.

| ID | Requirement | Implementation | Automated Evidence |
| --- | --- | --- | --- |
| URS-001 | Users access only their organization and assigned account scope. | `MedSupplierUserScope`, organization scoped querysets, object checks. | `test_auditor_reads_only_shared_records`, `test_cross_tenant_access_is_blocked`, `test_customer_detail_outside_account_scope_is_hidden` |
| URS-002 | Customer users never receive supplier private commercial fields. | Serializer field filtering and private field catalog. | `test_customer_quote_serializer_hides_private_commercial_fields`, `test_customer_roles_do_not_receive_private_financial_quote_fields` |
| URS-003 | Supplier finance can access private commercial financials. | Role-aware serializer context and cockpit permissions. | `test_supplier_finance_can_access_private_cockpit`, `test_supplier_finance_can_receive_private_financial_quote_fields` |
| URS-004 | Supplier quality/logistics do not receive financial private fields. | `can_view_private_financials` role logic. | `test_supplier_quality_and_logistics_do_not_receive_private_financial_quote_fields` |
| URS-005 | Read-only/customer roles cannot mutate supplier records. | `MedSupplierCanEdit`, `assert_can_mutate`. | `test_auditor_cannot_create_account`, `test_read_only_and_customer_roles_cannot_mutate_accounts` |
| URS-006 | Sensitive workflow actions require reason capture. | `_require_reason`, workflow actions. | `test_sensitive_action_requires_reason`, `test_document_obsolete_requires_reason_and_sets_obsolete_date` |
| URS-007 | Approvals/closures create audit/e-signature evidence. | `MedSupplierAuditEvent`, `MedSupplierESignature`. | `test_document_approve_changes_status_and_audits`, `test_workflow_transitions_change_status` |
| URS-008 | Document Room supports approval and obsolescence. | `SupplierDocumentViewSet.approve`, `obsolete`. | `test_document_approve_changes_status_and_audits`, `test_obsolete_document_cannot_be_approved` |
| URS-009 | Quote revisions preserve traceability and private supplier view. | `SupplierQuoteViewSet.revise`, quote metadata. | `test_quote_revise_clones_private_supplier_view_and_lines` |
| URS-010 | Quote approval blocks expired or incomplete quotes. | Quote approval validations. | `test_expired_quote_cannot_be_approved`, `test_quote_without_lines_cannot_be_approved` |
| URS-011 | Orders expose traceability across lines, lots, shipments, and inspections. | `purchase-orders/{id}/traceability`. | `test_purchase_order_traceability_returns_lines_lots_shipments_and_inspections` |
| URS-012 | CAPA closure requires root cause, action, effectiveness, and evidence. | `SupplierCAPAViewSet.close`. | `test_capa_without_required_evidence_cannot_be_closed` |
| URS-013 | CAPA action plans are auditable. | `SupplierCAPAViewSet.add_action`. | `test_capa_add_action_records_action_metadata_and_audit_trail` |
| URS-014 | Open CAPA blocks quality event closure. | `SupplierQualityEventViewSet.close`. | `test_quality_event_with_open_capa_cannot_be_closed` |
| URS-015 | FMEA risk score is calculated. | `SupplierFMEAItem.save`. | `test_fmea_item_calculates_risk_score` |
| URS-016 | Evidence packages cannot be empty and are exportable. | Evidence package validations and export action. | `test_evidence_package_empty_cannot_be_approved_or_exported`, `test_evidence_package_with_entry_exports`, `test_evidence_package_index_and_html_export_are_available` |
| URS-017 | Audit events for customers are read-only and redacted. | `MedSupplierAuditEventSerializer.get_fields`. | `test_customer_audit_trail_is_read_only_and_redacted` |
| URS-018 | AdminApps remains product access authority. | `validate_product_access`, AdminApps product endpoint. | `test_integration_status_declares_adminapps_as_authority`, AdminApps `ProductIntegrationContractTests` |
| URS-019 | Production-like health/readiness probes are public and minimal. | `/health`, `/ready`, `/api/health/`, `/api/ready/`. | `core.tests.ProductionLikeProbeTests` |
| URS-020 | CI/CD defines reproducible local-equivalent gates. | GitHub workflows and `CI_CD_PIPELINE.md`. | YAML parse and local command evidence in Stage 09 report |
