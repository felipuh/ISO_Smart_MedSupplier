# Security Overview

Date: 2026-06-29

## Security Model

- Tenant boundary: organization.
- Customer scope boundary: account.
- Role model: supplier and customer roles.
- Private commercial data guarded by backend serializers and querysets.
- Product access controlled by AdminApps.

## Controls

- JWT/SSO-based authentication.
- Server-side role and object checks.
- Explicit serializer fields.
- Customer redaction for audit detail.
- Reason capture for sensitive workflow actions.
- E-signature records for approvals/closures where implemented.
- Audit event records with correlation and hash metadata.
- Production-like security headers.
- Health/readiness probes with minimal output.

## Current Security Evidence

- Endpoint/role matrix tests.
- Serializer guardrail tests.
- Customer private-field hiding tests.
- Cross-tenant blocking tests.
- AdminApps product access tests.

## Limits

Security posture depends on deployment configuration, secret management, monitoring, patching, SOPs, and customer/company validation.
