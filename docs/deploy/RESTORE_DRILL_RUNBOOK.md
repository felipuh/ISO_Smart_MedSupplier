# Restore Drill Runbook

Date: 2026-06-30

Scope: PostgreSQL-only restore drill for ISO Smart MedSupplier.

## Status

Current status: BLOCKED BY DBA ACTION.

The application role `isosmart` cannot create databases. This is expected and secure. A DBA/operator must create an empty restore database owned by `isosmart`.

## Existing Backup Evidence

```text
ops_artifacts/backups/medsupplier_postgres_20260630_133620.dump
ops_artifacts/backups/medsupplier_media_20260630_133620.tar.gz
ops_artifacts/backups/medsupplier_20260630_133620.sha256
```

Checksum verification:

```bash
sha256sum -c ops_artifacts/backups/medsupplier_20260630_133620.sha256
```

Result observed:

```text
medsupplier_postgres_20260630_133620.dump: OK
medsupplier_media_20260630_133620.tar.gz: OK
```

## DBA Preparation

Run as a PostgreSQL role allowed to create databases:

```sql
CREATE DATABASE medsupplier_restore_drill_YYYYMMDD_HHMMSS OWNER isosmart;
```

Template:

```text
scripts/operations/dba_create_restore_drill_db.sql
```

## Restore Execution

```bash
RESTORE_DB_NAME=medsupplier_restore_drill_YYYYMMDD_HHMMSS RESTORE_DB_PRECREATED=true \
  scripts/operations/restore_drill_postgres.sh ops_artifacts/backups/medsupplier_postgres_20260630_133620.dump
```

## Acceptance Checklist

- Restore DB exists and is owned by `isosmart`.
- `pg_restore` exits 0.
- `database_probe=ok`.
- `manage.py check` exits 0 against restored DB.
- `manage.py migrate --plan` reports no planned operations.
- Sample pilot tenant can be queried.
- Unauthorized tenant/account access remains blocked.
- Restore evidence report saved under `ops_artifacts/restore/`.

## Failure Criteria

- Restore DB cannot be created or accessed.
- `pg_restore` fails.
- Migration plan is non-empty unexpectedly.
- Application check fails.
- Tenant scoping or AdminApps entitlement behavior differs from source.

## Cleanup

After evidence approval:

```sql
DROP DATABASE medsupplier_restore_drill_YYYYMMDD_HHMMSS;
```

Never drop `isosmart_main`.
