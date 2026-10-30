# Technical Design Specification

Date: 2026-06-29

## Architecture

MedSupplier is a Django REST Framework backend with a React/Vite frontend. AdminApps is the authority for organizations, users, roles, entitlements, product access, billing state, and commercial packaging.

## Tenant And Account Boundaries

- Organization is the supplier tenant boundary.
- Account is the customer scope boundary.
- Customer users require an active `MedSupplierUserScope` with an account.
- Supplier users can be organization-wide or role-scoped depending on role and data visibility.

## Security Controls

- JWT/SSO authentication.
- Server-side authorization before UI filtering.
- Explicit serializer fields.
- Private commercial field catalog.
- Queryset filtering by MedSupplier context.
- Object-level authorization checks.
- Production-like security headers.
- Public minimal health/readiness probes.

## Workflow Controls

- Sensitive actions require reason.
- Approval/closure actions create audit events and e-signatures where applicable.
- Audit events include correlation ID and hash chain support.
- Evidence packages include checksum metadata and export actions.

## Integration Design

- MedSupplier calls AdminApps product access validation.
- Business denials from AdminApps are not bypassed.
- Local fallback is explicit and disabled in production-like settings.

## Limitations

- HTML export is PDF-ready but does not generate binary PDF.
- Restore drill evidence is not yet executed.
- This TDS supports validation planning; it is not a formal validation approval.
