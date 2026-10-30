# DBA Restore Drill Handoff

Date: 2026-06-30

Scope: create an isolated PostgreSQL restore-drill database for MedSupplier.

## Reason

The application role `isosmart` is intentionally not allowed to create databases. This is correct for production security, but it means the restore drill needs one DBA/operator action before `pg_restore` can run.

## DBA Action

Run as a PostgreSQL role with database creation privileges:

```sql
CREATE DATABASE medsupplier_restore_drill_YYYYMMDD_HHMMSS OWNER isosmart;
```

Template:

```text
scripts/operations/dba_create_restore_drill_db.sql
```

## Operator Follow-Up

After the database exists:

```bash
RESTORE_DB_NAME=medsupplier_restore_drill_YYYYMMDD_HHMMSS RESTORE_DB_PRECREATED=true \
  scripts/operations/restore_drill_postgres.sh ops_artifacts/backups/<postgres-dump>.dump
```

Expected result:

```text
database_probe=ok
System check identified no issues
No planned migration operations
restore_result=PASS
```

## Cleanup

After evidence is captured and approved:

```sql
DROP DATABASE medsupplier_restore_drill_YYYYMMDD_HHMMSS;
```

Only drop the drill database. Never run cleanup commands against `isosmart_main`.
