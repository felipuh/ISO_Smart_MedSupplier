# Controlled Production Readiness Report

Date: 2026-06-29 16:09 CST

Scope:
- ISO Smart MedSupplier controlled commercial production readiness.
- AdminApps as real product, entitlement, billing, and organization authority.
- Deployment controls for a controlled pilot or production-like non-regulated tenant.

This report does not declare regulated production readiness and does not replace formal customer/company validation.

## Executive Decision

Status: CONDITIONALLY READY FOR CONTROLLED PRODUCTION PRE-GO-LIVE.

Controlled production is viable for a limited pilot or production-like non-regulated customer tenant only after the pre-go-live conditions below are completed and approved.

Approved scope:
- Controlled demo.
- Paid pilot.
- Limited customer tenant.
- Controlled enterprise MVP operation.
- Production-like non-regulated operation with explicit customer acceptance.

Not approved:
- Regulated production use.
- Claims of formal validation.
- Claims of regulatory compliance.
- Broad customer rollout.

## Pre-Go-Live Conditions

The following items must be completed before live customer operation:

| Condition | Required Result | Status |
| --- | --- | --- |
| Target environment approval | Named host, domain, TLS, DNS, reverse proxy, database, storage, and operator ownership approved. | PENDING |
| Secrets | Production secrets stored outside git and injected by approved environment or secret manager. | READY BY PROCESS |
| AdminApps real authority | AdminApps reachable from MedSupplier with fallback disabled. | PASS LOCAL TARGET, REPEAT FINAL TARGET |
| Billing | Billing/subscription state active for pilot tenant in AdminApps. | READY BY PROCESS |
| Entitlements | `MEDSUPPLIER` entitlement enabled for pilot tenant in AdminApps. | READY BY PROCESS |
| Monitoring/logging | Health, readiness, AdminApps integration, 5xx rate, disk, backup, and smoke monitors configured. | DOCUMENTED |
| Backups | Backup job configured and first artifact/checksum recorded. | PENDING TARGET ENV |
| Restore drill | Restore into isolated target/staging environment and evidence captured. | PENDING |
| Rollback drill | Rollback path rehearsed or formally accepted with owner approval. | PENDING |
| Domain/SSL | HTTPS termination active and verified; `X-Forwarded-Proto` passed to Django. | PENDING TARGET ENV |
| Human approval | Release owner/customer owner approval signed. | PENDING |

## Readiness Matrix

| Requirement | Status | Evidence / Notes |
| --- | --- | --- |
| Production-like environment | READY BY DESIGN | `docs/deploy/DEPLOYMENT_RUNBOOK.md`; production-like `check --deploy` only reports HSTS preload opt-in warning. |
| Secure secrets | READY BY PROCESS | `backend/.env.example` documents environment-driven secrets; production settings reject unsafe defaults where applicable. |
| AdminApps real | PASS LOCAL TARGET, FINAL TARGET SMOKE REQUIRED | `check_medsupplier_adminapps --no-fallback` passed against local AdminApps target with product entitlement source `adminapps`. Final staging/production target must repeat this. |
| Billing basic operational | READY BY ADMINAPPS CONTRACT | AdminApps products/billing/user/API tests pass; commercial docs define billing owner and model. |
| Entitlements operational | READY | AdminApps product entitlement tests pass; MedSupplier integration denies access when AdminApps denies or is unavailable without approved fallback. |
| MedSupplier operational | PASS | Django check passes; RC evidence includes backend tests, frontend lint/build, and E2E 5/5. |
| Monitoring basic | DOCUMENTED | `docs/deploy/MONITORING_LOGGING_RUNBOOK.md`. |
| Logs | DOCUMENTED | Django logs via `ISOSMART_LOG_DIR`, systemd journal, and Nginx log expectations documented. |
| Backups | DOCUMENTED, TARGET SETUP PENDING | `docs/deploy/BACKUP_RESTORE_RUNBOOK.md`. |
| Restore tested | PENDING | Runbook exists; target restore drill evidence is still required before live operation. |
| Rollback tested | PENDING | Rollback plan exists; target rollback rehearsal or formal acceptance is required. |
| Domain/SSL | PENDING TARGET ENV | Deployment runbook and Nginx/systemd artifacts exist; final domain certificate validation must be done on host. |
| Nginx/systemd/Docker | PARTIAL READY | Nginx and systemd templates exist. Systemd now uses MedSupplier venv. `/health` and `/ready` proxy to the backend. Docker is not the selected local architecture. |
| Support policy | READY DRAFT | `docs/commercial/SUPPORT_MODEL_DRAFT.md`. |
| Onboarding | READY DRAFT | `docs/commercial/ONBOARDING_CHECKLIST.md`. |
| Manual operation | READY | `docs/deploy/TENANT_OPERATIONS_RUNBOOK.md` and `docs/internal/manual-operacion-por-roles.md`. |
| Demo tenant | READY BY SCRIPT/E2E | E2E suite seeds/uses demo workspace and passed 5/5 in RC evidence. |
| Customer tenant | READY BY PROCESS | Tenant setup documented; real customer tenant requires AdminApps entitlement, billing status, roles, scope, and support approval. |
| Runbooks | READY | Deployment, backup/restore, rollback, monitoring/logging, tenant operations, CI/CD. |

## Changes Applied In This Stage

Deployment corrections:
- `deploy/systemd/medsupplier-backend.service`
  - Updated Gunicorn path to use MedSupplier's own virtual environment:
    `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend/.venv312/bin/gunicorn`.
- `deploy/nginx/medsupplier.conf`
  - `/health` now proxies to the MedSupplier backend instead of returning static text.
  - `/ready` now proxies to the MedSupplier backend readiness endpoint.

Operational documentation added:
- `docs/deploy/MONITORING_LOGGING_RUNBOOK.md`
- `docs/deploy/TENANT_OPERATIONS_RUNBOOK.md`
- `docs/release/TARGET_ENVIRONMENT_GATE_EVIDENCE.md`

Dependency correction:
- `backend/requirements.txt` now includes `reportlab==4.4.10` and `openpyxl==3.1.5` because core report exports import these packages and `core.tests` failed without them.

## Validation Evidence

Commands executed:

```bash
test -x backend/.venv312/bin/gunicorn
rg -n "<legacy-isosmart-venv-path>|return 200 \"OK\"|location /ready|proxy_pass http://medsupplier_backend" deploy/systemd/medsupplier-backend.service deploy/nginx/medsupplier.conf
backend/.venv312/bin/python backend/manage.py check --settings=backend.settings_test
# Sensitive production-like values configured out of band.
ENVIRONMENT=production DATABASE_ENGINE=sqlite SECURE_HSTS_PRELOAD=false backend/.venv312/bin/python backend/manage.py check --deploy
BILLING_SCHEDULER_ENABLED=false .venv312/bin/python manage.py check --settings=config.settings_test
BILLING_SCHEDULER_ENABLED=false .venv312/bin/python manage.py shell --settings=config.settings_test -c "from django.test import Client; c=Client(HTTP_HOST='localhost'); r=c.get('/api/integration/health/', **{'integration auth header': '[REDACTED_EXAMPLE_VALUE]'}); print(r.status_code); print(r.content.decode())"
```

Results:
- MedSupplier Gunicorn path exists.
- No active systemd reference to ISO Smart virtual environment remains in the MedSupplier unit.
- Nginx no longer returns static `/health`; `/health` and `/ready` proxy to backend.
- MedSupplier Django check: no issues.
- MedSupplier production-like deploy check: only `security.W021`, accepted because HSTS preload remains domain-level opt-in.
- AdminApps Django check: no issues.
- AdminApps integration smoke: PASS with `--no-fallback`; source `adminapps`, reason `ok`.
- Local `/health` and `/ready` endpoints return HTTP 200.
- `core.tests` pass after declaring and installing report export dependencies.

Nginx validation note:
- Direct `nginx -t -c deploy/nginx/medsupplier.conf` is not valid because the file is a deploy snippet containing `upstream`/`server` context, not a complete root `nginx.conf`.
- The snippet was validated from a temporary `http` context with `$connection_upgrade` map and unprivileged listen ports; syntax test passed.
- Final host validation must include this file from the real `http` context and define the expected `$connection_upgrade` map.

Target local service note:
- The live local process on port `8002` has working directory `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend`, but was started with the legacy ISO Smart virtualenv. The systemd template is corrected to use MedSupplier's own venv. The target host must be restarted/reloaded with the corrected unit before controlled production approval.

## Controlled Go / No-Go

Conditional Go for:
- Internal controlled demo.
- Paid pilot setup.
- Customer pilot dry run.
- Production-like non-regulated pre-go-live validation.

No-Go until completed:
- Live customer operation without target backup artifact and restore drill evidence.
- Live customer operation without SSL/domain verification.
- Live customer operation without final target AdminApps no-fallback smoke.
- Any regulated production claim.
- Any formal validation claim without signed customer/company validation.

## Pilot Operating Limits

- Use only approved tenant data.
- Keep AdminApps as the authority for access, entitlements, and billing state.
- Keep local fallback disabled outside tests.
- Keep support, escalation, and rollback owners named.
- Run daily health/readiness/AdminApps smoke checks during pilot.
- Record incidents, deployments, backups, restore drills, and approvals.

## Known Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Restore drill not yet executed in target environment | High | Execute restore drill before live customer operation. |
| Rollback not rehearsed on target host | High | Rehearse rollback or get explicit release-owner acceptance. |
| TLS/domain not validated on target host | High | Verify certificate, DNS, proxy headers, CORS, and CSRF origins. |
| AdminApps reachable locally but not from final host | High | Run target integration smoke before go-live. |
| HSTS preload enabled too early | Medium | Keep preload disabled until domain/subdomain policy and rollback impact are approved. |
| Secrets handled manually | Medium | Use environment manager or secret manager; do not store secrets in repo. |
| Logs capturing sensitive data | Medium | Review logs using monitoring/logging runbook. |

## Final Decision

Decision: CONTROLLED PRODUCTION IS PREPARED, WITH PRE-GO-LIVE CONDITIONS.

The ecosystem is prepared for controlled commercial production planning and limited pilot operation. It can proceed to target-environment setup, pilot tenant configuration, and pre-go-live validation.

It must not be treated as regulated production or broadly released until restore, rollback, SSL/domain, target AdminApps smoke, backup evidence, and human approval are complete.
