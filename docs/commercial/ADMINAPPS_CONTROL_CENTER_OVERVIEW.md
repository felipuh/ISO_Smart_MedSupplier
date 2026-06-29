# AdminApps Control Center Overview

Date: 2026-06-29

## Purpose

AdminApps is the product-neutral control center for the Smart3AI ecosystem. It manages organizations, users, roles, products, entitlements, billing state, product access, and suspension.

## Why It Matters

MedSupplier should not decide commercial access by itself in production-like operation. AdminApps provides a central authority so the ecosystem can sell products separately or bundled without duplicating access and billing logic in every product.

## Key Controls

- Organization lifecycle.
- User and role administration.
- Product catalog.
- Product entitlements.
- Subscription and billing status.
- Product access validation endpoint.
- Legacy module compatibility where needed.

## MedSupplier Contract

MedSupplier calls AdminApps for product access validation. Business denials from AdminApps are not bypassed. Local fallback is explicit and disabled in production-like settings.

## Deployment Note

AdminApps must be reachable by MedSupplier in production-like environments. If AdminApps is unavailable, MedSupplier should fail closed rather than silently grant product access.
