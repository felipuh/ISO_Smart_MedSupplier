# Traceability Matrix

| Requirement | Implementation | Test Evidence |
| --- | --- | --- |
| Account scoped Customer access | `MedSupplierUserScope`, queryset filtering | `test_auditor_reads_only_shared_records` |
| Private commercial fields hidden | Explicit serializers | `test_customer_quote_serializer_hides_private_commercial_fields` |
| Supplier cockpit protected | `/cockpit/private/` | cockpit Customer/Supplier tests |
| E-signature reason required | workflow actions | `test_sensitive_action_requires_reason` |
| Evidence package cannot be empty | EvidencePackage actions | evidence package tests |
| FMEA risk score | `SupplierFMEAItem.save` | FMEA risk score test |
