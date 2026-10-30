# AdminApps Integration Decision

Date: 2026-06-29

## Decision

AdminApps remains the authority for organization, user, role, entitlement, product access, subscription/billing status, and product-neutral packaging.

## Rationale

- Keeps MedSupplier independently sellable without duplicating identity and billing authority.
- Prevents silent local entitlement bypass in production-like operation.
- Preserves a single control center for product activation and suspension.

## Implemented Controls

- MedSupplier calls AdminApps product access validation.
- AdminApps business denials are not bypassed.
- Local fallback is explicit and disabled for production-like settings.
- Integration status exposes product access source and fallback state.

## Evidence

- MedSupplier `MedSupplierAdminAppsClientTests`.
- AdminApps `ProductSystemEntitlementTests`.
- AdminApps `ProductIntegrationContractTests`.
- `docs/internal/ADMINAPPS_MEDSUPPLIER_CONTRACT.md`.

## Approval State

Technical decision prepared. Human release approval remains pending.
