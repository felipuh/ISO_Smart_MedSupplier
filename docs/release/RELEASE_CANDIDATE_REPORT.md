# Release Candidate Report

Date: 2026-06-29 14:59 CST

Scope:
- ISO Smart ecosystem positioning and validation package.
- MedSupplier backend, frontend, E2E demo runtime, enterprise module surface, role matrix, and AdminApps integration.
- AdminApps product authority, entitlements/billing related services, and integration smoke.

## Executive Decision

Status: RC CANDIDATE - CONDITIONAL GO FOR CONTROLLED REVIEW.

Go:
- Controlled demo.
- Controlled POC.
- Paid pilot.
- Controlled enterprise MVP review.
- Production-like non-regulated review, subject to environment-specific deployment approval.

No-Go:
- Regulated production use.
- Claims of formal regulatory compliance.
- Claims that the system is validated.
- Customer production rollout without signed human review, customer validation evidence, backup/restore drill evidence, and environment approval.

Reasoning:
- Automated gates passed for MedSupplier backend, MedSupplier frontend lint/build, MedSupplier E2E, AdminApps backend/product authority tests, migrations, integration smoke, and documentation claim scan.
- The validation package, release notes, rollback plan, backup/restore runbook, known issues, CI/CD definition, endpoint/role matrix, and production-like hardening docs are present.
- Human approval and formal customer validation remain pending by design.

## Gate Summary

| Gate | Status | Evidence |
| --- | --- | --- |
| Worktrees controlled | PASS | `git status --short` clean in `ISO_Smart_MedSupplier` and `adminapps` before this report. |
| MedSupplier backend check | PASS | `backend/.venv312/bin/python backend/manage.py check --settings=backend.settings_test` -> no issues. |
| MedSupplier migrations | PASS | `backend/.venv312/bin/python backend/manage.py makemigrations --check --dry-run --settings=backend.settings_test` -> no changes detected. |
| MedSupplier backend tests | PASS | `backend/.venv312/bin/python backend/manage.py test core.tests.ProductionLikeProbeTests medsupplier --settings=backend.settings_test` -> 48 tests OK. |
| MedSupplier frontend lint | PASS | `npm run lint` in `frontend` -> exit 0. |
| MedSupplier frontend build | PASS | `npm run build` in `frontend` -> exit 0, production bundle generated. |
| MedSupplier E2E | PASS | `npm run test:e2e:medsupplier` -> 5 passed. |
| AdminApps backend check | PASS | `BILLING_SCHEDULER_ENABLED=false .venv312/bin/python manage.py check --settings=config.settings_test` -> no issues. |
| AdminApps migrations | PASS | `BILLING_SCHEDULER_ENABLED=false .venv312/bin/python manage.py makemigrations --check --dry-run --settings=config.settings_test` -> no changes detected. |
| AdminApps products/entitlements/billing tests | PASS | `BILLING_SCHEDULER_ENABLED=false .venv312/bin/python manage.py test apps.products apps.billing apps.users apps.api --settings=config.settings_test` -> 123 tests OK. |
| AdminApps smoke real | PASS | Django test client request to `/api/integration/health/` with `X-API-Key` and permitted host -> HTTP 200, integration service ok. |
| No silent fallback | PASS | AdminApps integration defaults fail-closed outside test settings; tests cover explicit fallback only under controlled test configuration. |
| Endpoint/role matrix | PASS | Covered by MedSupplier endpoint role matrix tests and documented in `docs/internal/MEDSUPPLIER_ENDPOINT_ROLE_MATRIX.md`. |
| Production-like hardening | PASS WITH JUSTIFICATION | Production-like `check --deploy` passes with only `security.W021`; HSTS preload remains opt-in until domain ownership, HTTPS, subdomain policy, and rollback windows are approved. |
| CI/CD defined | PASS | `.github/workflows/medsupplier-ci.yml`, AdminApps CI workflow, and `docs/deploy/CI_CD_PIPELINE.md`. |
| Validation Package | PASS | `docs/validation/VALIDATION_PACKAGE_INDEX.md` and linked SRS/FRS/TDS/test/risk/SOP/review artifacts. |
| Release notes | PASS | `docs/release/RELEASE_NOTES.md` and `docs/release/CHANGE_LOG.md`. |
| Rollback plan | PASS | `docs/deploy/ROLLBACK_PLAN.md`. |
| Backup/restore docs | PASS | `docs/deploy/BACKUP_RESTORE_RUNBOOK.md` and `docs/validation/Backup_Restore_Evidence.md`. |
| Known issues | PASS | `docs/release/KNOWN_ISSUES.md`. |
| Human review | PENDING | Template exists in `docs/validation/Human_Review_Approval_Template.md`; approval must be signed before production claims or regulated use. |

## Command Evidence

MedSupplier:

```bash
backend/.venv312/bin/python backend/manage.py check --settings=backend.settings_test
backend/.venv312/bin/python backend/manage.py makemigrations --check --dry-run --settings=backend.settings_test
backend/.venv312/bin/python backend/manage.py test core.tests.ProductionLikeProbeTests medsupplier --settings=backend.settings_test
cd frontend && npm run lint
cd frontend && npm run build
cd frontend && npm run test:e2e:medsupplier
# Sensitive production-like values configured out of band.
ENVIRONMENT=production DATABASE_ENGINE=sqlite SECURE_HSTS_PRELOAD=false backend/.venv312/bin/python backend/manage.py check --deploy
```

Results:
- `check`: no issues.
- `makemigrations --check --dry-run`: no changes detected.
- Backend tests: 48 tests OK.
- Frontend lint: exit 0.
- Frontend build: exit 0.
- E2E: 5 passed.
- Production-like deploy check: only `security.W021` for HSTS preload opt-in.

AdminApps:

```bash
BILLING_SCHEDULER_ENABLED=false .venv312/bin/python manage.py check --settings=config.settings_test
BILLING_SCHEDULER_ENABLED=false .venv312/bin/python manage.py makemigrations --check --dry-run --settings=config.settings_test
BILLING_SCHEDULER_ENABLED=false .venv312/bin/python manage.py test apps.products apps.billing apps.users apps.api --settings=config.settings_test
BILLING_SCHEDULER_ENABLED=false .venv312/bin/python manage.py shell --settings=config.settings_test -c "from django.test import Client; c=Client(HTTP_HOST='localhost'); r=c.get('/api/integration/health/', **{'integration auth header': '[REDACTED_EXAMPLE_VALUE]'}); print(r.status_code); print(r.content.decode())"
# Sensitive production-like values configured out of band.
ENVIRONMENT=production DATABASE_ENGINE=sqlite SECURE_HSTS_PRELOAD=false BILLING_SCHEDULER_ENABLED=false .venv312/bin/python manage.py check --deploy
```

Results:
- `check`: no issues.
- `makemigrations --check --dry-run`: no changes detected.
- Backend/product authority tests: 123 tests OK.
- Integration smoke: HTTP 200, `{"status": "ok", "service": "Admin Apps Integration", "version": "1.0"}`.
- Production-like deploy check: only `security.W021` for HSTS preload opt-in.

Documentation claim scan:

```bash
rg -n "<forbidden-claim-regex>" docs/commercial docs/validation docs/compliance docs/security docs/release || true
```

Result:
- No forbidden claim matches.

## Evidence Map

Core evidence:
- `docs/internal/STAGE_00_BASELINE_FREEZE_REPORT.md`
- `docs/internal/ECOSYSTEM_VALIDATION_CONTRACT.md`
- `docs/internal/MEDSUPPLIER_REPRODUCIBLE_ENVIRONMENT.md`
- `docs/internal/STAGE_03_E2E_EVIDENCE.md`
- `docs/internal/ADMINAPPS_MEDSUPPLIER_CONTRACT.md`
- `docs/internal/STAGE_05_ADMINAPPS_INTEGRATION_EVIDENCE.md`
- `docs/internal/MEDSUPPLIER_ENDPOINT_ROLE_MATRIX.md`
- `docs/internal/STAGE_07_ENTERPRISE_MODULE_COMPLETION.md`
- `docs/internal/STAGE_08_PRODUCTION_LIKE_HARDENING_REPORT.md`
- `docs/internal/STAGE_09_CI_CD_PIPELINE_REPORT.md`
- `docs/internal/STAGE_10_VALIDATION_PACKAGE_REPORT.md`
- `docs/internal/STAGE_11_COMMERCIAL_READINESS_REPORT.md`

Release and operations evidence:
- `docs/release/RELEASE_NOTES.md`
- `docs/release/CHANGE_LOG.md`
- `docs/release/KNOWN_ISSUES.md`
- `docs/deploy/DEPLOYMENT_RUNBOOK.md`
- `docs/deploy/ROLLBACK_PLAN.md`
- `docs/deploy/BACKUP_RESTORE_RUNBOOK.md`
- `docs/deploy/CI_CD_PIPELINE.md`
- `docs/security/PRODUCTION_LIKE_HARDENING.md`

Validation evidence:
- `docs/validation/VALIDATION_PACKAGE_INDEX.md`
- `docs/validation/Traceability_Matrix.md`
- `docs/validation/Test_Plan.md`
- `docs/validation/Test_Evidence.md`
- `docs/validation/E2E_Evidence.md`
- `docs/validation/Endpoint_Role_Matrix_Evidence.md`
- `docs/validation/AdminApps_Integration_Decision.md`
- `docs/validation/Human_Review_Approval_Template.md`
- `docs/validation/Backup_Restore_Evidence.md`

Commercial evidence:
- `docs/commercial/PRODUCT_BRIEF_MEDSUPPLIER.md`
- `docs/commercial/PRODUCT_BRIEF_ISO_SMART.md`
- `docs/commercial/ECOSYSTEM_OVERVIEW.md`
- `docs/commercial/ADMINAPPS_CONTROL_CENTER_OVERVIEW.md`
- `docs/commercial/SALES_FAQ.md`
- `docs/commercial/SCOPE_AND_LIMITATIONS.md`
- `docs/commercial/RELEASE_STAGE_POSITIONING.md`

## Gaps

1. Human review is pending.
   - Required before any final release approval or production claim.

2. Formal customer validation is pending.
   - Required before regulated customer use or claims that customer workflows are validated.

3. Backup/restore drill evidence is pending.
   - Runbook exists; timestamped restore proof must be captured for production approval.

4. HSTS preload remains intentionally disabled.
   - Current status is justified for RC because preload requires domain/subdomain policy approval and rollback analysis.

5. Environment-specific deployment signoff is pending.
   - Secrets, DNS, TLS, reverse proxy, storage, backups, monitoring, and alerting must be reviewed in the target environment.

6. Binary evidence export remains scoped as future work if required by buyers.
   - HTML/index evidence exports exist; PDF/signature workflow should remain buyer/validation dependent.

## Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Overstating compliance in sales or delivery | High | Use approved language only; retain forbidden claim scan and commercial scope docs. |
| Treating RC as validated production | High | Keep decision as conditional RC; require signed human review and validation execution. |
| Environment drift from local evidence | Medium | Use CI/CD, deployment runbook, environment checklist, and production-like checks per environment. |
| Backup/restore assumptions unproven in target infra | Medium | Execute restore drill and attach evidence before production approval. |
| HSTS preload decision made too early | Medium | Keep preload opt-in until domain and rollback strategy are approved. |
| AdminApps integration key management | Medium | Use managed secrets, rotation policy, and environment-specific API keys. |

## Final RC Decision

Decision: CONDITIONAL GO AS RELEASE CANDIDATE.

The ecosystem can be declared a Release Candidate for controlled review, controlled demo, POC, paid pilot, and controlled enterprise MVP evaluation.

The ecosystem must not be declared validated, regulatory compliant, or approved for regulated production use until the pending human review, customer validation evidence, backup/restore drill, and environment deployment signoff are complete.
