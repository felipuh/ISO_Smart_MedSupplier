# ADR: MedSupplier Enterprise MVP

Date: 2026-06-27

## Decision
ISO Smart MedSupplier remains a Django/DRF and React/Vite vertical product integrated with Iso Smart conventions and AdminApps authority. The MVP adds MedSupplier-specific RBAC/ABAC, customer account scope, explicit serializers, audit-ready event hashing, e-signature support, evidence packages, FMEA, line-level quote/order tracking, and private Supplier cockpit APIs.

## Context
The previous baseline was a functional MVP with generic Iso Smart roles, simple `shared/private` visibility, serializers using broad model exposure, and limited audit trail. This was insufficient for a controlled Supplier-Customer regulated demo because Customer users could not be modeled with account-specific scope and private Supplier commercial data needed stronger protection.

## Consequences
- AdminApps remains the identity and entitlement authority.
- `UserProfile` compatibility is preserved; `MedSupplierUserScope` adds domain roles and account scope.
- Backend authorization is enforced through queryset filtering, object checks, serializer field filtering, and action permissions.
- Compliance claims must remain “compliance-ready”, “audit-ready”, and “validation-supporting”; no certification is implied.
