# CI/CD Pipeline Contract

Date: 2026-06-29

Scope: Stage 9 reproducible validation pipeline for MedSupplier and AdminApps. ISO Smart core remains a separate product/repository validation concern.

## MedSupplier Pipeline

Workflow:

- `.github/workflows/medsupplier-ci.yml`

Jobs:

- Backend checks and tests.
- Frontend lint and build.
- MedSupplier E2E.

Backend commands:

```bash
python backend/manage.py check --settings=backend.settings_test
python backend/manage.py makemigrations --check --dry-run --settings=backend.settings_test
python backend/manage.py test core.tests.ProductionLikeProbeTests medsupplier --settings=backend.settings_test
python backend/manage.py check --deploy --settings=backend.settings
```

Frontend commands:

```bash
cd frontend
npm ci
npm run lint
npm run build
npx playwright install --with-deps chromium
npm run test:e2e:medsupplier
```

Production-like deploy check uses CI-only placeholder secrets and HTTPS origins. It does not use committed secrets.

## AdminApps Pipeline

Workflow:

- `/home/felipe/proyectos/adminapps/.github/workflows/adminapps-ci.yml`

Jobs:

- Backend product authority checks and tests.
- Frontend lint and build.

Backend commands:

```bash
cd /home/felipe/proyectos/adminapps/backend
python manage.py check --settings=config.settings_test
python manage.py makemigrations --check --dry-run --settings=config.settings_test
python manage.py test apps.products apps.billing apps.users apps.api --settings=config.settings_test
python manage.py check --deploy --settings=config.settings
```

Frontend commands:

```bash
cd /home/felipe/proyectos/adminapps/frontend
npm ci
npm run lint
npm run build
```

`BILLING_SCHEDULER_ENABLED=false` is set in CI to avoid starting background scheduler jobs during check/test process setup.

## Product Boundaries

- MedSupplier validates MedSupplier backend, frontend, E2E, hardening probes, and AdminApps client behavior through mocks/fallback tests.
- AdminApps validates product-neutral entitlement, billing, user, and API authority behavior.
- ISO Smart core pipelines remain separate. This Stage 9 does not merge ISO Smart core validation into MedSupplier CI.

## Required Branch Protection Signals

Recommended required checks for MedSupplier PRs:

- `Backend Checks And Tests`
- `Frontend Lint And Build`
- `MedSupplier E2E`

Recommended required checks for AdminApps PRs:

- `Backend Product Authority Tests`
- `Frontend Lint And Build`

## Residual Notes

- `check --deploy` currently reports the accepted HSTS preload warning (`security.W021`) unless `SECURE_HSTS_PRELOAD=True` is explicitly approved.
- AdminApps existing `.github/workflows/ci.yml` remains in place for legacy coverage. The new product-authority workflow is the Stage 9 canonical pipeline for AdminApps.
- Restore-drill evidence is outside CI until a safe staging dataset and artifact storage policy are approved.
