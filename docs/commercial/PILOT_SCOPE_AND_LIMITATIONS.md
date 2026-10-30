# Pilot Scope And Limitations - ISO Smart MedSupplier

Date: 2026-06-29

## Pilot Scope

The pilot may include:

- One controlled MedSupplier tenant.
- A limited set of supplier and customer users.
- AdminApps-controlled organization, product entitlement, subscription/billing state, and user access.
- Supplier/customer account scoping.
- Supplier-private commercial cockpit and financial field protections.
- Document approval/obsolescence workflow.
- RFQ/quote workflow with customer-safe views.
- Purchase order, shipment, inspection, lot, and traceability review.
- NCR/CAPA/FMEA quality workflow review.
- Evidence package creation and JSON/HTML export review.
- Weekly pilot checkpoint.

## Data Scope

Allowed:

- Seeded demo data.
- Synthetic data.
- Sanitized buyer-approved pilot data.
- Non-sensitive operational examples approved by the pilot owner.

Not allowed without written approval:

- Regulated production data.
- Patient data.
- Supplier confidential pricing not approved for pilot use.
- Customer confidential data outside the contracted tenant.
- Secrets, API keys, passwords, tokens, certificates, or private keys.

## Commercial Limitations

MedSupplier can be described as validation-ready and audit-ready. It must not be described as formally validated, regulated-production approved, or guaranteed to satisfy customer/company regulatory obligations.

## Technical Limitations

- Final target SSL/domain gate is pending before controlled production.
- Backup artifact/checksum is pending before controlled production.
- Restore drill is pending before controlled production.
- Rollback rehearsal or formal acceptance is pending before controlled production.
- Monitoring activation is pending before controlled production.
- Human approval is pending before controlled production.
- Binary PDF evidence export is future or buyer-specific scope.
- ISO Smart is separate and not included unless explicitly scoped.

## Required Contract Language

The pilot is controlled in scope. Live production use requires separate target-environment acceptance, backup/restore evidence, rollback readiness, monitoring activation, AdminApps no-fallback smoke, and human approval.
