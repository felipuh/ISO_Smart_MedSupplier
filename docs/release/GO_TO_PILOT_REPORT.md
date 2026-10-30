# Go-To-Pilot Report - ISO Smart MedSupplier

Date: 2026-06-30

## Decision

Decision: GO for MedSupplier paid pilot and controlled enterprise MVP with restrictions.

Not approved:
- Unrestricted ecosystem Release Candidate.
- Live controlled production.
- Full regulated production.
- Any formal validation or regulatory approval claim.

## Closed P1 Items

1. MedSupplier/AdminApps real integration smoke:
   - Closed for local target validation.
   - Command passed without fallback:
     `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e --no-fallback`
   - Evidence: `docs/release/ADMINAPPS_REAL_SMOKE_EVIDENCE.md`.

2. ISO Smart frontend lint:
   - Closed.
   - `npm run lint` PASS.
   - Evidence: `docs/release/ISOSMART_JOINT_SALE_READINESS_NOTE.md`.

3. ISO Smart E2E:
   - Closed.
   - `npm run test:e2e` PASS, 16/16.
   - Evidence: `docs/release/ISOSMART_JOINT_SALE_READINESS_NOTE.md`.

## Current Evidence Summary

MedSupplier:
- Backend check/migrations/tests: PASS.
- MedSupplier backend tests: PASS, 47 tests OK in latest pre-pilot run.
- Frontend lint/build: PASS.
- MedSupplier E2E: PASS, 5/5.
- Production-like deploy check: PASS with accepted HSTS preload warning.
- Real AdminApps smoke without fallback: PASS in local target configuration.

AdminApps:
- Product authority tests: PASS.
- Products, entitlements, billing, users, and integration APIs validated locally.
- Local target seed for `medsupplier-demo-e2e` exists and validates MedSupplier entitlement/billing access.

ISO Smart:
- Backend benchmark tests: PASS, 78 tests OK.
- Frontend lint/build: PASS.
- E2E benchmark: PASS, 16/16.

Commercial:
- Pilot package created under `docs/commercial/PILOT_*`.
- Sales scope, limitations, success criteria, support model, data classification, known limitations, onboarding checklist, and demo script are present.
- Commercial package claim scan: PASS.

## Stage 7 Cleanup

External-publication cleanup completed for release docs:
- Example secret-like values in release command evidence were replaced with neutral redacted markers.
- Commercial claim scan command no longer embeds sensitive keywords in a way that self-matches.

Known residuals:
- Code and tests still contain environment variable names, fixture passwords, and test API key strings. These are implementation/test fixtures and must not be copied into public collateral.
- Internal docs may still mention environment variable names as operational instructions.

## Remaining P2/P3 Items

Before first pilot kickoff:
- Commit and tag the controlled release set.
- Confirm pilot tenant entitlement and billing state in AdminApps.
- Confirm signed pilot scope, support owner, pilot owner, and success criteria.
- Run MedSupplier E2E immediately before kickoff.

Before controlled production:
- Complete SSL/domain/proxy validation in target environment.
- Produce backup artifact and checksum.
- Execute restore drill.
- Execute rollback rehearsal or approved rollback tabletop.
- Activate monitoring/logging checks.
- Run target AdminApps integration smoke without fallback.
- Obtain human release approval.

Before regulated production:
- Execute formal validation plan.
- Approve SOPs.
- Complete IQ/OQ/PQ or equivalent evidence.
- Complete training records, security audit, pen test, legal/regulatory review, and executive go/no-go.

## Approved Pilot Positioning

Approved:
- Controlled demo.
- Paid pilot.
- Controlled enterprise MVP.
- Validation-ready/audit-ready review package support.

Required wording:
- Controlled scope only.
- Customer/company validation remains required for regulated use.
- No live production use until target-environment acceptance is complete.
- No formal regulatory approval or guaranteed compliance claim.
