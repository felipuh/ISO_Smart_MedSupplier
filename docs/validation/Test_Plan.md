# Test Plan

Date: 2026-06-29

## Objective

Verify MedSupplier and AdminApps controls required for validation-ready and audit-ready human review.

## Scope

- MedSupplier backend checks, migration drift, role/security tests, workflow tests, evidence package tests, and production-like probes.
- MedSupplier frontend lint, build, and E2E runtime flow.
- AdminApps product-neutral entitlement, billing, users, API, check, migration drift, lint, and build.
- Production-like deploy checks with accepted HSTS preload warning.

## MedSupplier Commands

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier
backend/.venv312/bin/python backend/manage.py check --settings=backend.settings_test
backend/.venv312/bin/python backend/manage.py makemigrations --check --dry-run --settings=backend.settings_test
backend/.venv312/bin/python backend/manage.py test core.tests.ProductionLikeProbeTests medsupplier --settings=backend.settings_test
backend/.venv312/bin/python backend/manage.py check --deploy --settings=backend.settings
cd frontend
npm run lint
npm run build
npm run test:e2e:medsupplier
```

## AdminApps Commands

```bash
cd /home/felipe/proyectos/adminapps/backend
BILLING_SCHEDULER_ENABLED=false .venv312/bin/python manage.py check --settings=config.settings_test
BILLING_SCHEDULER_ENABLED=false .venv312/bin/python manage.py makemigrations --check --dry-run --settings=config.settings_test
BILLING_SCHEDULER_ENABLED=false .venv312/bin/python manage.py test apps.products apps.billing apps.users apps.api --settings=config.settings_test
BILLING_SCHEDULER_ENABLED=false .venv312/bin/python manage.py check --deploy --settings=config.settings
cd ../frontend
npm run lint
npm run build
```

## Acceptance

- All commands pass or have documented accepted warnings.
- Traceability matrix maps requirements to test evidence.
- Human review remains pending until signed approval.
