# Deployment Options

Date: 2026-06-29

## Option 1 - Controlled Demo

- Hosted or local demo environment.
- Seeded data or approved non-sensitive data.
- No regulated production claim.
- Best for buyer walkthroughs and workflow fit review.

## Option 2 - Paid Pilot / Proof Of Concept

- Limited scope.
- Defined success criteria.
- Realistic roles and workflows.
- AdminApps entitlement model enabled.
- Validation-ready evidence may be generated for review.

## Option 3 - Controlled Enterprise MVP

- Configured tenant model.
- Production-like hardening.
- CI/CD gates.
- Backup/restore runbooks.
- Human approval checklist.

## Option 4 - Production-Like Non-Regulated

- Approved infrastructure.
- Production-like settings.
- Monitoring and support model.
- Formal customer/company acceptance.
- Not positioned as regulated production validation unless customer validation is executed and approved.

## Required Shared Controls

- AdminApps reachable and authoritative.
- `DEBUG=False`.
- Product fallback disabled.
- Health/readiness probes.
- Backup/restore procedures.
- Rollback plan.
