# VPS Rollback Rehearsal Runbook

Date: 2026-06-30

Scope: safe rollback rehearsal for MedSupplier on the DigitalOcean VPS target.

## Status

Current status: READY-NOT-EXECUTED.

Blocker: final VPS and previous approved release artifact are not available.

## Prerequisites

- VPS provisioned.
- Current release deployed.
- Previous approved artifact or tag available.
- PostgreSQL backup generated immediately before rehearsal.
- Restore drill evidence available or DBA restore path approved.
- AdminApps target reachable.
- Maintenance window approved if rehearsal affects shared users.

## Pre-Rehearsal Backup

```bash
scripts/operations/backup_replica.sh
sha256sum -c ops_artifacts/backups/<checksum-file>.sha256
```

## Current Release Capture

```bash
git rev-parse HEAD
systemctl status medsupplier-backend --no-pager
curl -fsS https://medsupplier.<domain>/health
curl -fsS https://medsupplier.<domain>/ready
```

## Rollback Procedure

```bash
sudo systemctl stop medsupplier-backend
git fetch --tags
git checkout <previous-approved-tag-or-sha>
backend/.venv312/bin/python -m pip install -r backend/requirements.txt
cd frontend && npm ci && npm run build
cd ..
DJANGO_SETTINGS_MODULE=backend.settings backend/.venv312/bin/python backend/manage.py migrate --plan
sudo systemctl start medsupplier-backend
sudo systemctl reload nginx
```

## Validation

```bash
curl -fsS https://medsupplier.<domain>/health
curl -fsS https://medsupplier.<domain>/ready
DJANGO_SETTINGS_MODULE=backend.settings backend/.venv312/bin/python backend/manage.py check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e --no-fallback
```

## Success Criteria

- Service starts.
- Nginx serves frontend.
- `/health` and `/ready` pass.
- AdminApps no-fallback smoke passes.
- No unexpected migration plan.
- Pilot tenant can access allowed flows.
- Restricted roles remain restricted.

## Failure Criteria

- Service cannot start.
- Health/readiness fail.
- AdminApps entitlement smoke fails.
- Migration plan requires destructive or unexpected operations.
- Tenant scoping/RBAC regression appears.

## Roll Forward

If rollback fails:

```bash
git checkout <current-release-tag-or-sha>
backend/.venv312/bin/python -m pip install -r backend/requirements.txt
cd frontend && npm ci && npm run build
cd ..
sudo systemctl restart medsupplier-backend
sudo systemctl reload nginx
```

Record all results in the release evidence package.
