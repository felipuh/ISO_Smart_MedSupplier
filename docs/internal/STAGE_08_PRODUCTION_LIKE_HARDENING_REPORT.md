# Stage 08 - Production-Like Hardening Report

Date: 2026-06-29

## Objective

Prepare MedSupplier and AdminApps for controlled production-like operation without claiming formal regulated production validation.

## Changes

- MedSupplier production settings now force secure cookies when `ENVIRONMENT=production`.
- MedSupplier production settings now default SSL redirect and HSTS on in production.
- MedSupplier now emits explicit CSP `frame-ancestors` and Permissions-Policy headers.
- MedSupplier exposes public minimal health/readiness probes at `/health`, `/ready`, `/api/health/`, and `/api/ready/`.
- MedSupplier test settings explicitly disable SSL redirect/HSTS for local HTTP tests.
- AdminApps production settings now force secure cookies when `ENVIRONMENT=production`.
- AdminApps production settings now default SSL redirect and HSTS on in production.
- AdminApps now emits explicit CSP `frame-ancestors` and Permissions-Policy headers.
- `.env.example` files now include production-like security override blocks.

## Deliverables

- `docs/security/PRODUCTION_LIKE_HARDENING.md`
- `docs/deploy/DEPLOYMENT_RUNBOOK.md`
- `docs/deploy/BACKUP_RESTORE_RUNBOOK.md`
- `docs/deploy/ROLLBACK_PLAN.md`

## Verification

- `backend/.venv312/bin/python backend/manage.py check --deploy --settings=backend.settings`
  - Result: PASS with justified `security.W021`.
- `/home/felipe/proyectos/adminapps/backend/.venv312/bin/python manage.py check --deploy --settings=config.settings`
  - Result: PASS with justified `security.W021`.
- `backend/.venv312/bin/python backend/manage.py test core.tests.ProductionLikeProbeTests medsupplier --settings=backend.settings_test`
  - Result: PASS, 48 tests.

## Gate Decision

Approved with observations.

`security.W021` is accepted because `SECURE_HSTS_PRELOAD=True` should only be enabled after a domain-level preload decision. Enabling preload casually can make rollback harder across subdomains.

## Residual Risks

- HSTS preload remains opt-in.
- Backup/restore runbook is documented but still needs an executed restore drill artifact in a staging environment.
- AdminApps check starts its billing scheduler during Django setup; this is existing behavior and should be reviewed before service packaging.
- This is production-like readiness, not formal customer validation.
