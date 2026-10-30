# Stage 15 - Release Candidate / Controlled Go-Live Readiness Report

Date: 2026-06-30

Product: ISO Smart MedSupplier

Decision: RELEASE CANDIDATE COMMERCIAL CONTROLLED - GO WITH RESTRICTIONS.

## Executive Status

MedSupplier is commercially ready for controlled demo, paid pilot, and controlled enterprise MVP. It is not approved for live controlled production until the blocked operational gates are executed on a real target/VPS environment.

Updated readiness:

| Category | Status | Percent |
| --- | --- | ---: |
| Controlled demo | PASS | 100% |
| Paid pilot | PASS WITH RESTRICTIONS | 96% |
| Controlled enterprise MVP | PASS WITH RESTRICTIONS | 92% |
| Local PostgreSQL replica / VPS bridge | PASS WITH RESTRICTION | 92% |
| Live controlled production | PASS WITH RESTRICTIONS / NOT EXECUTED TARGET GATES | 74% |
| Formal regulated production | FAIL / NOT APPROVED | 35% |

## Ready

- MedSupplier backend check: PASS.
- MedSupplier migration drift: PASS.
- PostgreSQL runtime: PASS.
- AdminApps no-fallback entitlement smoke: PASS.
- Pilot tenant linked to AdminApps external ID: PASS.
- MEDSUPPLIER entitlement active: PASS.
- Backup artifact: PASS.
- Backup checksum: PASS.
- Local backend/frontend build gates: PASS.
- Rollback tabletop: PASS WITH RESTRICTION.
- Runbooks/checklists: PASS.

## Not Ready

- PostgreSQL restore drill: BLOCKED by DB privilege; requires DBA-created restore DB.
- DNS/domain: READY-NOT-EXECUTED.
- SSL/TLS: READY-NOT-EXECUTED.
- Real VPS rollback rehearsal: READY-NOT-EXECUTED.
- VPS monitoring/alerting: READY-NOT-EXECUTED.
- Human approval: PENDING.
- Commit/tag: PENDING.

## Commands Executed

```bash
DJANGO_SETTINGS_MODULE=backend.settings ./.venv312/bin/python manage.py check
DJANGO_SETTINGS_MODULE=backend.settings ./.venv312/bin/python manage.py makemigrations --check --dry-run
DJANGO_SETTINGS_MODULE=backend.settings ./.venv312/bin/python manage.py migrate --plan
DJANGO_SETTINGS_MODULE=backend.settings ./.venv312/bin/python manage.py check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e --no-fallback
DJANGO_SETTINGS_MODULE=config.settings BILLING_SCHEDULER_ENABLED=false ./.venv312/bin/python manage.py check
sha256sum -c ops_artifacts/backups/medsupplier_20260630_133620.sha256
DJANGO_SETTINGS_MODULE=backend.settings ./.venv312/bin/python manage.py check --deploy
npm run lint
npm run build
scripts/operations/backup_replica.sh
scripts/operations/restore_drill_postgres.sh ops_artifacts/backups/medsupplier_postgres_20260630_133620.dump
scripts/operations/smoke_replica.sh
scripts/operations/rollback_tabletop.sh
```

## Evidence

- `ops_artifacts/backups/medsupplier_postgres_20260630_133620.dump`
- `ops_artifacts/backups/medsupplier_media_20260630_133620.tar.gz`
- `ops_artifacts/backups/medsupplier_20260630_133620.sha256`
- `ops_artifacts/smoke/replica_smoke_report.txt`
- `ops_artifacts/restore/restore_drill_postgres_20260630_133731.txt`
- `ops_artifacts/rollback/rollback_tabletop_report.txt`
- `docs/release/LOCAL_REPLICA_OPERATIONAL_READINESS_REPORT.md`
- `docs/deploy/DBA_RESTORE_DRILL_HANDOFF.md`
- `docs/deploy/DIGITALOCEAN_VPS_BRIDGE_CHECKLIST.md`

## Blockers

| Gate | Status | Blocker | Required Action |
| --- | --- | --- | --- |
| PostgreSQL restore drill | BLOCKED | App DB role cannot create DB | DBA creates restore DB owned by `isosmart`; rerun restore script. |
| DNS/domain | READY-NOT-EXECUTED | No final domain/VPS IP | Create VPS, assign IP, add DNS records. |
| SSL/TLS | READY-NOT-EXECUTED | No final domain | Run Certbot after DNS propagation. |
| VPS rollback rehearsal | READY-NOT-EXECUTED | No VPS/previous artifact | Execute rehearsal on VPS using release artifact. |
| Monitoring/alerting | READY-NOT-EXECUTED | No VPS target | Activate minimum monitors on target. |
| Human approval | PENDING | Manual gate | Complete `HUMAN_APPROVAL_GATE.md`. |
| Commit/tag | PENDING | Requires release owner approval | Commit and tag after review. |

## Commercial Restrictions

- Do not claim formal regulated production.
- Do not claim guaranteed regulatory acceptance.
- Do not use live customer production data until target gates pass.
- Pilot contracts must include scope, data classification, support model, known limitations, and validation responsibility.

## Final Recommendation

Proceed as controlled commercial Release Candidate for demo, paid pilot, and controlled MVP. Do not approve live controlled production until DNS, SSL/TLS, restore drill, VPS rollback rehearsal, monitoring, and human approval are complete.
