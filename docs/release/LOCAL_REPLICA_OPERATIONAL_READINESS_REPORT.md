# Local Replica Operational Readiness Report

Date: 2026-06-30

Purpose: make this server a PostgreSQL-based local replica and bridge for a near-future DigitalOcean VPS production target.

## Decision

Status: LOCAL REPLICA READY WITH ONE DBA RESTRICTION.

Approved on this server:
- PostgreSQL backup artifact and checksum.
- MedSupplier/AdminApps no-fallback smoke using `backend.settings`.
- Health/readiness checks against local backend.
- Frontend lint/build.
- Rollback tabletop.
- Tenant readiness for `medsupplier-demo-e2e`.

Blocked on this server:
- Full PostgreSQL restore drill, because the application DB role `isosmart` does not have permission to create databases.

This is an operationally good security posture. The restore drill requires an operator/DBA to create an empty restore database owned by `isosmart`, then rerun the restore script.

## Strict Database Position

Operational replica evidence uses PostgreSQL only.

Confirmed MedSupplier runtime database:
- Engine: `django.db.backends.postgresql`
- Database: `isosmart_main`
- Host: `127.0.0.1`
- Port: `5432`
- User: `isosmart`

SQLite is allowed only inside automated test settings and is not accepted as replica, staging, pilot, or production evidence.

## Scripts Added

```text
scripts/operations/backup_replica.sh
scripts/operations/restore_drill_postgres.sh
scripts/operations/smoke_replica.sh
scripts/operations/rollback_tabletop.sh
scripts/operations/dba_create_restore_drill_db.sql
```

Restore drill settings:

```text
backend/backend/settings_restore_drill_postgres.py
```

## Evidence Generated

Backup:

```text
ops_artifacts/backups/medsupplier_postgres_20260630_133620.dump
ops_artifacts/backups/medsupplier_media_20260630_133620.tar.gz
ops_artifacts/backups/medsupplier_20260630_133620.sha256
ops_artifacts/backups/medsupplier_replica_20260630_133620.manifest.txt
```

Restore:

```text
ops_artifacts/restore/restore_drill_postgres_20260630_133731.txt
```

Result: BLOCKED.

Blocker:

```text
database role cannot create restore drill database
```

Required action:

```bash
createdb -O isosmart medsupplier_restore_drill_<timestamp>
RESTORE_DB_NAME=medsupplier_restore_drill_<timestamp> RESTORE_DB_PRECREATED=true \
  scripts/operations/restore_drill_postgres.sh ops_artifacts/backups/medsupplier_postgres_20260630_133620.dump
```

DBA handoff:

```text
docs/deploy/DBA_RESTORE_DRILL_HANDOFF.md
```

Smoke:

```text
ops_artifacts/smoke/replica_smoke_report.txt
```

Result: PASS.

Smoke covered:
- `manage.py check`
- `makemigrations --check --dry-run`
- `migrate --plan`
- AdminApps no-fallback entitlement validation
- `/health`
- `/ready`
- frontend lint
- frontend build

Rollback:

```text
ops_artifacts/rollback/rollback_tabletop_report.txt
```

Result: PASS WITH RESTRICTION.

Restriction: target/VPS rehearsal still required with a real previous approved artifact.

## Tenant Readiness

MedSupplier local PostgreSQL tenant:

```text
slug=medsupplier-demo-e2e
external_id=4d4e38a8-1f1b-4a2d-8295-0a7692a413ba
```

AdminApps target tenant:

```text
code=MEDSUPDEMO
status=active
MEDSUPPLIER entitlement=enabled active
subscription=active
```

## DigitalOcean VPS Handoff

Checklist:

```text
docs/deploy/DIGITALOCEAN_VPS_BRIDGE_CHECKLIST.md
```

When the VPS is created:

1. Install PostgreSQL and create the application database/user.
2. Restore from the latest `.dump` artifact.
3. Copy media artifact and extract into the approved media path.
4. Configure `.env` through secret management, not committed files.
5. Install systemd unit and Nginx site.
6. Point DNS to the VPS.
7. Install valid TLS certificate.
8. Run:

```bash
scripts/operations/smoke_replica.sh
scripts/operations/restore_drill_postgres.sh <latest-postgres-dump>
scripts/operations/rollback_tabletop.sh
```

9. Replace tabletop rollback with an actual previous-artifact rehearsal before live production.
10. Capture human approval.

## Remaining Gates

Still pending for live controlled production:
- DNS/domain.
- Valid SSL/TLS certificate.
- PostgreSQL restore drill after DBA-created restore DB or target role with controlled create permission.
- Real rollback rehearsal on VPS.
- Monitoring/alerting activation on VPS.
- Human approval.

## Additional Local Verifications

Checksum verification:

```text
medsupplier_postgres_20260630_133620.dump: OK
medsupplier_media_20260630_133620.tar.gz: OK
```

Deploy check:

```text
DJANGO_SETTINGS_MODULE=backend.settings manage.py check --deploy
```

Result:

```text
PASS with only security.W021 for HSTS preload opt-in.
```

Local listeners:

```text
127.0.0.1:5432 PostgreSQL
127.0.0.1:8000 AdminApps gunicorn
127.0.0.1:8002 MedSupplier gunicorn
```
