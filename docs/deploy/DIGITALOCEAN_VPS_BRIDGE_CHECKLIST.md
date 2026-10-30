# DigitalOcean VPS Bridge Checklist

Date: 2026-06-30

Purpose: promote the local PostgreSQL replica work into a DigitalOcean VPS target without changing release scope.

## Provision

- Create VPS.
- Create non-root deployment user.
- Install system packages: Python 3.12, Node/npm, PostgreSQL client tools, Nginx, certbot, git.
- Configure firewall: SSH, HTTP, HTTPS only.
- Add SSH keys for approved operators.

## Database

- Create PostgreSQL database and application user.
- Restore latest `medsupplier_postgres_*.dump`.
- Run:

```bash
DJANGO_SETTINGS_MODULE=backend.settings backend/.venv312/bin/python backend/manage.py check
DJANGO_SETTINGS_MODULE=backend.settings backend/.venv312/bin/python backend/manage.py migrate --plan
```

## Application

- Clone approved release tag/commit.
- Create `.env` from secret manager or protected deployment notes.
- Install backend dependencies.
- Build frontend.
- Install systemd service from `deploy/systemd/medsupplier-backend.service`.
- Install Nginx site from `deploy/nginx/medsupplier.conf`.

## Smoke

Run:

```bash
scripts/operations/smoke_replica.sh
```

Required:
- Django check PASS.
- Migration plan clean.
- AdminApps no-fallback PASS.
- `/health` PASS.
- `/ready` PASS.
- frontend lint/build PASS.

## Restore Drill

Run:

```bash
scripts/operations/backup_replica.sh
scripts/operations/restore_drill_postgres.sh ops_artifacts/backups/<postgres-dump>.dump
```

If the app DB role cannot create databases, use `docs/deploy/DBA_RESTORE_DRILL_HANDOFF.md`.

## DNS And TLS

- Point approved domain/subdomain to VPS.
- Install TLS certificate.
- Verify HTTPS redirect.
- Decide HSTS preload only after rollback policy is approved.

## Production-Control Approval

Do not approve live controlled production until:
- DNS/TLS PASS.
- Backup/checksum PASS.
- Restore drill PASS.
- Rollback rehearsal PASS.
- Monitoring/alerting active.
- AdminApps target smoke PASS without fallback.
- Human release approval signed.
