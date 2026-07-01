# Monitoring And Alerting Runbook

Date: 2026-06-30

Scope: minimum practical monitoring for paid pilot and controlled go-live.

## Status

Current status: READY-NOT-EXECUTED FOR VPS.

Local process/listener checks are available. VPS alerting is pending.

## Minimum Checks

| Check | Command / Signal | Warning | Critical |
| --- | --- | --- | --- |
| HTTP health | `curl -fsS https://medsupplier.<domain>/health` | 2 failures | 5 failures / 5 min |
| HTTP readiness | `curl -fsS https://medsupplier.<domain>/ready` | 2 failures | 5 failures / 5 min |
| PostgreSQL connectivity | `pg_isready` or Django DB probe | 2 failures | 5 failures |
| AdminApps entitlement | `check_medsupplier_adminapps --no-fallback` | 1 failure | 2 failures |
| Nginx status/logs | `systemctl status nginx`, error log | repeated 4xx/5xx | Nginx down |
| Disk usage | `df -h` | >75% | >90% |
| CPU/RAM | `top`, `free -m`, node exporter | sustained >75% | sustained >90% |
| SSL expiry | `openssl x509 -checkend` | <30 days | <7 days |
| Backend error rate | Django/gunicorn logs | >1% 5xx | >5% 5xx |
| Frontend error rate | Nginx + browser reports if enabled | spike | broad user impact |

## Simple Initial Option

Use a lightweight cron/systemd timer plus email/Slack webhook once available.

Example health script:

```bash
#!/usr/bin/env bash
set -euo pipefail
curl -fsS https://medsupplier.<domain>/health >/dev/null
curl -fsS https://medsupplier.<domain>/ready >/dev/null
DJANGO_SETTINGS_MODULE=backend.settings backend/.venv312/bin/python backend/manage.py check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e --no-fallback >/dev/null
```

## Incident Classes

| Class | Description | Response |
| --- | --- | --- |
| P0 | Data exposure, tenant isolation failure, total outage, unauthorized financial/private access | Stop release/use, disable affected access, notify owners immediately. |
| P1 | Health/readiness down, AdminApps entitlement unavailable, login broadly failing | Triage within 30 minutes; rollback/fix-forward decision. |
| P2 | Single module degraded, warnings, backup late, disk warning | Triage within 1 business day or pilot SLA. |

## P0 Runbook

1. Stop or isolate affected service.
2. Preserve logs and request IDs.
3. Notify Product Owner, Technical Owner, Security/Compliance, Operations.
4. Verify tenant/account scope.
5. Decide rollback or controlled maintenance.
6. Document timeline, impact, containment, corrective action.

## P1 Runbook

1. Check health/readiness.
2. Check AdminApps smoke.
3. Check PostgreSQL connectivity.
4. Check latest deployment/config change.
5. Review Nginx/gunicorn/Django logs.
6. Fix forward or rollback.

## Pilot Minimum Checklist

- Health monitor active.
- Readiness monitor active.
- Disk usage monitor active.
- SSL expiry monitor active after TLS.
- AdminApps no-fallback smoke scheduled.
- Backup job evidence reviewed.
- Incident owner assigned.
