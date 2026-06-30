# Monitoring And Logging Runbook

Date: 2026-06-29

Scope: controlled production monitoring and logging for ISO Smart MedSupplier with AdminApps as product authority.

## Objectives

- Detect application availability issues quickly.
- Detect AdminApps entitlement or billing authority failures.
- Preserve enough operational evidence for incident review.
- Avoid storing secrets or sensitive regulated content in logs.

## Minimum Monitors

| Monitor | Target | Expected |
| --- | --- | --- |
| MedSupplier health | `GET /health` | HTTP 200. |
| MedSupplier readiness | `GET /ready` | HTTP 200 and database ready. |
| AdminApps integration health | `GET /api/integration/health/` with `X-API-Key` | HTTP 200. |
| Product entitlement smoke | `check_medsupplier_adminapps --organization-slug <slug> --no-fallback` | Product enabled for pilot tenant through AdminApps, no local fallback. |
| Frontend static app | `GET /` | HTTP 200. |
| Login smoke | Approved test account in demo or pilot tenant | Login succeeds. |
| Role smoke | Customer/viewer role attempts restricted action | HTTP 403. |

## Suggested Alert Thresholds

| Signal | Warning | Critical |
| --- | --- | --- |
| `/ready` failure | 2 consecutive failures | 5 consecutive failures or 5 minutes. |
| AdminApps integration failure | 2 consecutive failures | 5 consecutive failures. |
| 5xx rate | More than 1 percent for 10 minutes | More than 5 percent for 5 minutes. |
| Login failures | Sudden spike above baseline | Repeated lockouts or broad login failure. |
| Disk usage | 75 percent | 90 percent. |
| Backup job | Late by 1 expected interval | Missing backup after approved RPO window. |

## Log Locations

MedSupplier Django logging is configured through `ISOSMART_LOG_DIR`; default path:

```text
backend/logs/ai/django.log
```

Systemd service logs:

```bash
journalctl -u medsupplier-backend.service --since "1 hour ago"
```

Nginx logs depend on host configuration; expected paths:

```text
/var/log/nginx/access.log
/var/log/nginx/error.log
```

## Log Review Checklist

- Confirm every incident has a timestamp, request ID, tenant or organization context where safe, and affected endpoint.
- Confirm no API keys, JWTs, passwords, reset tokens, or customer confidential content are logged.
- Confirm repeated authorization denials are reviewed for possible misconfiguration or malicious behavior.
- Confirm AdminApps entitlement failures are treated as access-blocking unless an approved maintenance procedure exists.

## Daily Controlled Production Checks

```bash
curl -fsS https://medsupplier.smart3ai.local/health
curl -fsS https://medsupplier.smart3ai.local/ready
backend/.venv312/bin/python backend/manage.py check_medsupplier_adminapps --organization-slug <pilot-org-slug> --settings=backend.settings
```

For staging/production target checks, include `--no-fallback`:

```bash
backend/.venv312/bin/python backend/manage.py check_medsupplier_adminapps --organization-slug <pilot-org-slug> --no-fallback --settings=backend.settings
```

Record:
- Operator.
- Timestamp.
- Commands.
- Result.
- Deviations.

## Incident Triage

1. Confirm user-visible symptom and affected tenant.
2. Check `/health` and `/ready`.
3. Check AdminApps integration health and entitlement state.
4. Review recent deployment, migration, or configuration change.
5. Review application and proxy logs by request ID and timestamp.
6. Decide: fix forward, rollback, or controlled maintenance window.
7. Record corrective action and post-incident follow-up.

## Retention

- Keep operational logs according to customer contract and data classification.
- Keep incident evidence at least through pilot closure.
- Keep deployment, backup, restore, and rollback evidence with release artifacts.
