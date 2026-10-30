# Ecosystem Overview

Date: 2026-06-29

## Components

| Component | Purpose |
| --- | --- |
| ISO Smart | Core ISO-oriented management-system workspace. |
| MedSupplier | Supplier-Customer control tower for regulated supplier collaboration. |
| AdminApps | Product-neutral control center for organizations, users, entitlements, billing, and access. |

## Commercial Architecture

MedSupplier can be sold as:

- standalone product with AdminApps as authority,
- bundle with ISO Smart,
- paid pilot,
- proof of concept,
- controlled enterprise MVP,
- production-like non-regulated deployment after review.

## Authority Boundaries

- AdminApps owns organizations, users, product access, entitlements, billing status, and suspension.
- MedSupplier owns supplier/customer operational domain records.
- ISO Smart owns broad ISO management-system workflows.

## Current Readiness

- MedSupplier backend and E2E evidence exist.
- AdminApps product-neutral entitlement evidence exists.
- CI/CD pipelines are defined.
- Production-like hardening is documented.
- Validation package is prepared for human review.

## Required Before Regulated Production Use

- Human release approval.
- Customer/company validation.
- SOP alignment.
- Restore drill evidence.
- Deployment environment approval.
