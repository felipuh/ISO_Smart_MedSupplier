# Target Environment Gate Evidence

Date: 2026-06-29 16:09 CST

## Scope

Stage 4 evidence for ISO Smart MedSupplier controlled production preparation.

This document prepares and records target-environment gates. It does not approve live controlled production.

## Decision

Controlled production: NOT APPROVED YET.

Reason:

- Final SSL/domain target is not verified.
- Final backup artifact and checksum are not recorded.
- Restore drill is not executed.
- Rollback rehearsal or formal release-owner acceptance is not executed.
- Monitoring activation is documented but not confirmed active on final target.
- Human approval is not signed.

## Gate Matrix

| Gate | Status | Evidence | Required Before Controlled Production |
| --- | --- | --- | --- |
| SSL/domain target | PENDING FINAL TARGET | Deployment runbook defines HTTPS/proxy requirements. | Verify DNS, certificate, CORS/CSRF, proxy headers, and HSTS policy on final host. |
| Nginx config | PASS LOCAL TEMPLATE | Snippet syntax validated in temporary `http` context with `$connection_upgrade` map and unprivileged listen ports. | Run `nginx -t` on final host with real include path and ports. |
| systemd service | PASS TEMPLATE, RESTART REQUIRED | `deploy/systemd/medsupplier-backend.service` uses MedSupplier venv and backend working directory. | Install/reload/restart target unit and verify process uses MedSupplier venv. |
| Environment variables | PARTIAL | Runbook defines production-like env and `ADMIN_APPS_ALLOW_LOCAL_FALLBACK=False`. | Record approved target env without printing secrets. |
| Secret management | READY BY PROCESS | Runbooks require environment/secret manager, not committed files. | Confirm target secret injection owner and storage. |
| Backup artifact | PENDING FINAL TARGET | Backup runbook exists. | Produce target backup artifact before go-live. |
| Backup checksum | PENDING FINAL TARGET | Backup runbook includes `sha256sum`. | Record SHA256 checksum for the approved artifact. |
| Restore drill | PENDING | Restore runbook exists. | Restore to isolated target/staging DB and validate readiness/AdminApps/tenant access. |
| Rollback rehearsal | PENDING | Rollback plan exists. | Rehearse rollback or record formal release-owner acceptance. |
| Monitoring activation | DOCUMENTED, PENDING ACTIVATION | Monitoring/logging runbook defines checks and thresholds. | Activate monitors and record dashboard/alert ownership. |
| Logging | DOCUMENTED | Log locations and review checklist documented. | Confirm final log paths, retention, and no secret leakage. |
| Healthcheck | PASS LOCAL | `GET /health` returned HTTP 200 locally. | Verify final HTTPS endpoint. |
| Readiness check | PASS LOCAL | `GET /ready` returned HTTP 200 locally. | Verify final HTTPS endpoint. |
| AdminApps real smoke without fallback | PASS LOCAL TARGET | `check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e --no-fallback` passed. | Repeat in final staging/production target with pilot tenant. |
| Human approval template | PENDING | Validation package includes human approval template. | Obtain signed release/customer owner approval. |

## Commands Executed

| Area | Command | Result | Observation |
| --- | --- | --- | --- |
| Nginx | Temporary `nginx -t` with `deploy/nginx/medsupplier.conf` included from an `http` context | PASS | Syntax OK using temporary unprivileged listen ports and temp paths. |
| systemd | `test -x backend/.venv312/bin/gunicorn` | PASS | MedSupplier Gunicorn binary exists. |
| systemd | `rg ... deploy/systemd/medsupplier-backend.service deploy/nginx/medsupplier.conf` | PASS | Template points to MedSupplier venv; nginx proxies `/health` and `/ready`. |
| Local probes | `curl -fsS -H 'Host: medsupplier.smart3ai.local' http://127.0.0.1:8002/health` | PASS | HTTP 200, service reports healthy. |
| Local probes | `curl -fsS -H 'Host: medsupplier.smart3ai.local' http://127.0.0.1:8002/ready` | PASS | HTTP 200, database ready. |
| MedSupplier backend | production-like `manage.py check --deploy` | PASS WITH JUSTIFICATION | Only HSTS preload warning. |
| MedSupplier backend | `DJANGO_SETTINGS_MODULE=backend.settings_test manage.py check` | PASS | No issues. |
| MedSupplier backend | `DJANGO_SETTINGS_MODULE=backend.settings_test manage.py migrate --plan` | PASS | No planned migration operations. |
| MedSupplier backend | `DJANGO_SETTINGS_MODULE=backend.settings_test manage.py test core.tests` | PASS AFTER DEPENDENCY FIX | 63 tests OK after adding/installing report export dependencies. |
| AdminApps target | `DJANGO_SETTINGS_MODULE=config.settings manage.py check` | PASS | No issues. |
| AdminApps target | `DJANGO_SETTINGS_MODULE=config.settings manage.py migrate --plan` | PASS | No planned migration operations. |
| AdminApps smoke | `check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e --no-fallback` | PASS | Source `adminapps`, entitlement enabled, reason `ok`. |

## Findings

### Closed During Stage 4

- Backend report export dependencies were missing from `backend/requirements.txt`.
- `core.tests` initially failed with missing `reportlab` and `openpyxl`.
- Added:
  - `reportlab==4.4.10`
  - `openpyxl==3.1.5`
- Installed both into `.venv312`.
- Re-ran `core.tests`: PASS, 63 tests OK.

### Still Open

- Final target process must be started from the corrected MedSupplier systemd unit. The local process on port `8002` uses the MedSupplier working directory but legacy ISO Smart virtualenv.
- Final target SSL/domain verification is not executed.
- Target backup artifact/checksum is not created.
- Restore drill is not executed.
- Rollback rehearsal is not executed.
- Monitoring is documented but not confirmed active.
- Human approval is not signed.

## Final Stage 4 Gate

Stage 4 status: PREPARED WITH OPEN TARGET GATES.

Approved:

- Continue paid pilot preparation.
- Continue controlled enterprise MVP preparation.
- Proceed to commercial pilot package with restrictions.

Not approved:

- Live controlled production.
- Full regulated production.
- Unrestricted ecosystem Release Candidate.
