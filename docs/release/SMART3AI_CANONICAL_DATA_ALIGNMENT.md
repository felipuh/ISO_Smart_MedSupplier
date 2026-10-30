# Smart3AI Canonical Data Alignment

Date: 2026-06-30

## Purpose

Align local enterprise replica data so Smart3AI is the owner organization for:

- ISO Smart
- ISO Smart MedSupplier
- AdminApps

This document records the local data correction performed for access validation and commercial readiness work. It does not claim regulated production validation.

## Canonical Organization

| Field | Value |
| --- | --- |
| Organization name | Smart3AI |
| Organization code | SMART3AI |
| Canonical domain | isosmart-ai.com |
| Billing status | Owner organization, payment-exempt |
| Products owned | ISO Smart, ISO Smart MedSupplier, AdminApps |

## Canonical User

| Field | Value |
| --- | --- |
| Email | fugalde@isosmart-ai.com |
| Role in AdminApps | superadmin |
| Role in ISO Smart / MedSupplier database | staff/superuser with Smart3AI profile |
| MedSupplier scope | supplier_admin |
| Organization | Smart3AI |

Password values are intentionally not documented here.

## Data Changes Applied

### ISO Smart / MedSupplier Database

Database:

```text
isosmart_main
```

Actions:

- Renamed/canonicalized organization `smart3ai` to `Smart3AI`.
- Set organization email to the canonical owner email.
- Migrated local owner login identity from the prior local email to `fugalde@isosmart-ai.com`.
- Reset local owner password for browser validation.
- Ensured owner user is active, staff, and superuser.
- Ensured active Smart3AI `UserProfile`.
- Ensured active MedSupplier `supplier_admin` scope for Smart3AI.
- Disabled duplicate old local owner identity if present outside the canonical user record.

### AdminApps Database

Database:

```text
adminapps_db
```

Actions:

- Canonicalized organization `SMART3AI` to `Smart3AI`.
- Set organization website to `https://isosmart-ai.com`.
- Marked organization metadata as owner/payment-exempt.
- Migrated local owner login identity to `fugalde@isosmart-ai.com`.
- Ensured owner user is active, verified, staff, superuser, and `superadmin`.
- Ensured primary `UserOrganization` membership for Smart3AI.
- Ensured active owner entitlements for:
  - `ISO_SMART`
  - `MEDSUPPLIER`
- Marked entitlement metadata as owner/payment-exempt.

## Validation Evidence

Commands executed:

```bash
curl -X POST http://medsupplier.isosmart.local/api/auth/login/
curl -X POST http://adminapps.isosmart.local/api/auth/login/
curl -X POST http://isosmart.local/api/auth/login/
```

Results:

| System | Login Result | Token Result |
| --- | --- | --- |
| ISO Smart MedSupplier | 200 PASS | access/refresh returned |
| AdminApps | 200 PASS | access/refresh returned |
| ISO Smart | 200 PASS | access/refresh returned |

AdminApps entitlement validation:

| Product | Enabled | Status | Billing |
| --- | --- | --- | --- |
| ISO Smart | true | active | owner/payment-exempt |
| ISO Smart MedSupplier | true | active | owner/payment-exempt |

## Notes

- Demo and E2E records were not deleted because they are part of local QA, release, and audit evidence.
- The canonical login for owner validation is now `fugalde@isosmart-ai.com`.
- Browser sessions using old tokens should clear local storage before re-testing.
