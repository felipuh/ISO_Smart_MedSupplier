# Release Notes - MedSupplier Controlled Release Candidate

Date: 2026-06-30

Release type: Controlled commercial Release Candidate.

Recommended tag: `medsupplier-rc-2026-06-30`

Recommended branch: `release/medsupplier-controlled-rc-2026-06-30`

## Summary

This Release Candidate prepares ISO Smart MedSupplier for controlled demo, paid pilot, and controlled enterprise MVP operations with AdminApps as the authority for organizations, users, billing, and entitlements.

## Included

- AdminApps no-fallback product entitlement smoke.
- PostgreSQL local replica/bridge scripts.
- PostgreSQL backup artifact and checksum workflow.
- Restore drill script with DBA handoff.
- Rollback tabletop workflow.
- DigitalOcean VPS bridge checklist.
- DNS/SSL go-live runbook.
- Monitoring/alerting runbook.
- Human approval gate.
- Release Candidate checklist.

## Validation Snapshot

- Backend check: PASS.
- Migration drift: PASS.
- PostgreSQL runtime: PASS.
- AdminApps no-fallback smoke: PASS.
- Frontend lint/build: PASS.
- Backup checksum: PASS.
- Deploy check: PASS with HSTS preload warning only.

## Known Restrictions

- PostgreSQL restore drill requires DBA-created restore database.
- DNS/domain not configured.
- SSL/TLS not configured.
- VPS rollback rehearsal not executed.
- Monitoring/alerting not activated on VPS.
- Human approval pending.

## Not Included

- Formal regulated production validation.
- Guaranteed regulatory compliance claim.
- Live production approval.
- HSTS preload activation.
- New MedSupplier product features.

## Recommended Commit Message

```text
chore(release): prepare MedSupplier controlled RC go-live readiness

- add PostgreSQL replica/backup/restore/rollback operations
- document DNS, SSL, VPS rollback, monitoring, and human approval gates
- record Stage 15 controlled go-live readiness evidence
- preserve AdminApps authority and no-fallback entitlement validation
```
