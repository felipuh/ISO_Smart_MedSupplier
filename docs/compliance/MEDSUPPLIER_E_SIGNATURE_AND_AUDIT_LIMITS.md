# MedSupplier E-Signature and Audit Trail Limits

Date: 2026-07-03

## Current Controls

- Sensitive MedSupplier workflow actions require a business reason and password reauthentication before an electronic signature is recorded.
- The signature is always bound to the authenticated user from the request, not to client-submitted user fields.
- Tenant/account scope is enforced before a signature is created.
- Audit events are chained with SHA-256 hashes and can be checked with `MedSupplierAuditEvent.verify_chain(organization_id)`.

## Limits

- The audit hash chain detects local DB tampering, but it is not WORM storage.
- A database administrator with direct write access can still alter rows unless external append-only/WORM controls exist.
- These controls support compliance workflows and audit-ready evidence, but they do not make the system formally validated or automatically compliant with 21 CFR Part 11, GxP, FDA, or any regulated production framework.

## Future Gate

Before regulated production use, add an externally controlled append-only/WORM evidence store, formal validation protocol, SOP approval, training evidence, backup/restore evidence, release approval, and customer/company acceptance.
