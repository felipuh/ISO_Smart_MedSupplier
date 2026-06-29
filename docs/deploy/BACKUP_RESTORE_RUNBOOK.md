# Backup And Restore Runbook

Date: 2026-06-29

Scope: production-like backup and restore procedures for MedSupplier and AdminApps. Commands are templates and must be adapted to the approved database names, hosts, and secret-management process.

## Backup Principles

- Back up before every deployment and migration.
- Store backups outside the application host.
- Encrypt backups at rest.
- Restrict restore permissions to approved operators.
- Record backup filename, checksum, timestamp, operator, source commit, and database version.

## PostgreSQL Backup

MedSupplier:

```bash
pg_dump --format=custom --no-owner --no-acl \
  --host "$DB_HOST" --port "$DB_PORT" --username "$DB_USER" \
  --file "medsupplier_$(date +%Y%m%d_%H%M%S).dump" "$DB_NAME"
```

AdminApps:

```bash
pg_dump --format=custom --no-owner --no-acl \
  --host "$ADMINAPPS_DB_HOST" --port "$ADMINAPPS_DB_PORT" --username "$ADMINAPPS_DB_USER" \
  --file "adminapps_$(date +%Y%m%d_%H%M%S).dump" "$ADMINAPPS_DB_NAME"
```

Checksum:

```bash
sha256sum *.dump
```

## Media / Uploads Backup

```bash
tar --create --gzip --file "medsupplier_media_$(date +%Y%m%d_%H%M%S).tar.gz" backend/media
sha256sum medsupplier_media_*.tar.gz
```

## Restore Drill

Restore only into an isolated staging database unless an emergency restore has been approved.

```bash
createdb "$RESTORE_DB_NAME"
pg_restore --clean --if-exists --no-owner --no-acl \
  --dbname "$RESTORE_DB_NAME" "medsupplier_YYYYMMDD_HHMMSS.dump"
```

Then validate:

```bash
backend/.venv312/bin/python backend/manage.py check --settings=backend.settings
backend/.venv312/bin/python backend/manage.py migrate --plan --settings=backend.settings
curl -fsS https://staging-medsupplier.smart3ai.local/ready
```

## Restore Acceptance

- Application starts without migration drift.
- Readiness endpoint is healthy.
- AdminApps integration can validate product access.
- A sampled tenant/account/document/quote/evidence package can be read by an authorized user.
- Unauthorized tenant access remains blocked.

## Evidence

Each restore drill must record:

- Backup artifact name and checksum.
- Restore target.
- Operator.
- Start/end time.
- Validation commands and result.
- Known deviations.
