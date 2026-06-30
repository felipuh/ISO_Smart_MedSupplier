# Deployment Runbook

Date: 2026-06-29

Scope: controlled production-like deployment for ISO Smart MedSupplier plus AdminApps authority services.

## Preconditions

- Tagged release or approved commit SHA.
- Clean dependency install from pinned requirements/package lock files.
- Database backup completed before deploy.
- AdminApps reachable from MedSupplier.
- `ADMIN_APPS_ALLOW_LOCAL_FALLBACK=False`.
- HTTPS termination configured at reverse proxy or load balancer.
- Secrets supplied by environment or secret manager, not committed files.

## MedSupplier Backend

1. Set production-like environment:

```bash
ENVIRONMENT=production
DEBUG=False
ALLOWED_HOSTS=medsupplier.smart3ai.local,medsupplier.isosmart.local
CORS_ALLOWED_ORIGINS=https://medsupplier.smart3ai.local
CSRF_TRUSTED_ORIGINS=https://medsupplier.smart3ai.local
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
ADMIN_APPS_ALLOW_LOCAL_FALLBACK=False
```

2. Install and validate:

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier
backend/.venv312/bin/python backend/manage.py check --deploy --settings=backend.settings
backend/.venv312/bin/python backend/manage.py makemigrations --check --dry-run --settings=backend.settings
backend/.venv312/bin/python backend/manage.py migrate --plan --settings=backend.settings
```

3. Apply migrations only after review:

```bash
backend/.venv312/bin/python backend/manage.py migrate --settings=backend.settings
```

4. Validate probes:

```bash
curl -fsS https://medsupplier.smart3ai.local/health
curl -fsS https://medsupplier.smart3ai.local/ready
```

## MedSupplier Frontend

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier/frontend
npm ci
npm run lint
npm run build
```

Publish only the generated build artifact through the approved static hosting or reverse proxy path.

## AdminApps Backend

1. Set production-like environment:

```bash
ENVIRONMENT=production
DEBUG=False
ALLOWED_HOSTS=adminapps.smart3ai.local,adminapps.isosmart.local
CORS_ALLOWED_ORIGINS=https://adminapps.smart3ai.local,https://medsupplier.smart3ai.local
CSRF_TRUSTED_ORIGINS=https://adminapps.smart3ai.local,https://medsupplier.smart3ai.local
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

2. Validate:

```bash
cd /home/felipe/proyectos/adminapps/backend
.venv312/bin/python manage.py check --deploy --settings=config.settings
.venv312/bin/python manage.py makemigrations --check --dry-run --settings=config.settings
.venv312/bin/python manage.py migrate --plan --settings=config.settings
```

3. Apply migrations only after review:

```bash
.venv312/bin/python manage.py migrate --settings=config.settings
```

## Reverse Proxy Notes

- Terminate TLS at Nginx/load balancer.
- Forward `X-Forwarded-Proto: https`.
- Proxy `/health` and `/ready` without authentication.
- Keep application APIs protected by JWT/API-key controls.
- Do not expose Django debug pages.
- Validate the Nginx snippet from a real `http` context and define the `$connection_upgrade` map before enabling the site.

## Post-Deploy Smoke Tests

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier
backend/.venv312/bin/python backend/manage.py check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e --no-fallback --settings=backend.settings
cd frontend && npm run test:e2e:medsupplier
```

## Go / No-Go

Go only if:

- Deploy checks pass with no critical warnings.
- AdminApps product access returns allowed for entitled organizations.
- MedSupplier fallback is disabled in production.
- Health/readiness probes pass.
- Smoke tests pass or deviations are formally accepted.
- Backup artifact/checksum, restore drill, rollback rehearsal, monitoring activation, and human approval are recorded before live controlled production.
