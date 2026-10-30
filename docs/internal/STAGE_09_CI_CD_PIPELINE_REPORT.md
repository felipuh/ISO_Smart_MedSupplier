# Stage 09 - CI/CD And Release Pipeline Report

Date: 2026-06-29

## Objective

Create reproducible CI pipelines for MedSupplier and AdminApps without merging product boundaries or depending on local developer state.

## Implemented

### MedSupplier

- Added `.github/workflows/medsupplier-ci.yml`.
- Backend job:
  - dependency install from `backend/requirements.txt`,
  - Django check,
  - migration drift check,
  - production-like probe and MedSupplier tests,
  - `check --deploy` with CI production-like env.
- Frontend job:
  - `npm ci`,
  - lint,
  - build.
- E2E job:
  - installs backend/frontend dependencies,
  - installs Playwright Chromium,
  - runs `npm run test:e2e:medsupplier` with `backend.settings_test`.

### AdminApps

- Added `/home/felipe/proyectos/adminapps/.github/workflows/adminapps-ci.yml`.
- Backend job:
  - dependency install from `backend/requirements.txt`,
  - Django check,
  - migration drift check,
  - product authority tests for `apps.products`, `apps.billing`, `apps.users`, `apps.api`,
  - `check --deploy` with CI production-like env.
- Frontend job:
  - `npm ci`,
  - lint,
  - build.
- CI disables the billing scheduler with `BILLING_SCHEDULER_ENABLED=false`.

## Documentation

- Added `docs/deploy/CI_CD_PIPELINE.md`.

## Verification

Local equivalent commands executed:

- MedSupplier:
  - `backend/.venv312/bin/python backend/manage.py check --settings=backend.settings_test`
  - `backend/.venv312/bin/python backend/manage.py makemigrations --check --dry-run --settings=backend.settings_test`
  - `backend/.venv312/bin/python backend/manage.py test core.tests.ProductionLikeProbeTests medsupplier --settings=backend.settings_test`
  - `backend/.venv312/bin/python backend/manage.py check --deploy --settings=backend.settings`
  - `cd frontend && npm run lint`
  - `cd frontend && npm run build`
  - `cd frontend && npm run test:e2e:medsupplier`
- AdminApps:
  - `/home/felipe/proyectos/adminapps/backend/.venv312/bin/python manage.py check --settings=config.settings_test`
  - `/home/felipe/proyectos/adminapps/backend/.venv312/bin/python manage.py makemigrations --check --dry-run --settings=config.settings_test`
  - `/home/felipe/proyectos/adminapps/backend/.venv312/bin/python manage.py test apps.products apps.billing apps.users apps.api --settings=config.settings_test`
  - `/home/felipe/proyectos/adminapps/backend/.venv312/bin/python manage.py check --deploy --settings=config.settings`
  - `cd /home/felipe/proyectos/adminapps/frontend && npm run lint`
  - `cd /home/felipe/proyectos/adminapps/frontend && npm run build`
- Workflow YAML parsing:
  - MedSupplier workflow parsed successfully with PyYAML.
  - AdminApps workflow parsed successfully with PyYAML.

## Gate Decision

Approved with observations.

## Observations

- `security.W021` remains accepted as in Stage 8.
- ISO Smart core pipeline remains intentionally separate.
- AdminApps frontend lint exits successfully but reports existing warnings. These are non-blocking for Stage 9 and should be handled as frontend hygiene before making lint warning-free a protected branch rule.
- AdminApps `settings_test` now disables SSL redirect/HSTS explicitly so local and CI tests do not inherit production redirects from a developer `.env`.
