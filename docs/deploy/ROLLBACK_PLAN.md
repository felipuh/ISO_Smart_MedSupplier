# Rollback Plan

Date: 2026-06-29

Scope: rollback for production-like MedSupplier/AdminApps deployments.

## Rollback Triggers

- Failed health/readiness after deployment.
- Critical authentication, entitlement, or tenant isolation regression.
- Migration failure or unexpected data-shape issue.
- AdminApps product access unavailable in production with no approved maintenance window.
- E2E smoke test failure on critical MedSupplier flows.

## Application Rollback

1. Stop traffic or drain instance from load balancer.
2. Re-deploy the last approved artifact or commit SHA.
3. Restart services.
4. Validate:

```bash
curl -fsS https://medsupplier.smart3ai.local/health
curl -fsS https://medsupplier.smart3ai.local/ready
```

5. Run smoke checks:

```bash
backend/.venv312/bin/python backend/manage.py check --deploy --settings=backend.settings
```

## Database Rollback

Prefer forward fixes when migrations have already modified production data. Use restore only when approved by release owner and data owner.

Restore decision requires:

- Last known good backup checksum.
- Confirmed recovery point objective.
- List of data written after backup that may be lost.
- Approval from release owner.

## Feature / Config Rollback

Configuration-only rollback may be enough for:

- CORS/CSRF origin mistakes.
- AdminApps base URL mistake.
- SSL/HSTS misconfiguration before browser preload.
- Rate limit too strict.

For MedSupplier production-like rollback, keep:

```bash
ADMIN_APPS_ALLOW_LOCAL_FALLBACK=False
DEBUG=False
```

Do not enable local fallback in production as a rollback shortcut.

## Communication

Record:

- Incident start time.
- Affected service.
- User-visible impact.
- Commit/config rolled back to.
- Validation evidence.
- Follow-up corrective action.

## Rollback Rehearsal Evidence

Before controlled production, record:

| Field | Value |
| --- | --- |
| Environment |  |
| Current release artifact/SHA |  |
| Previous approved artifact/SHA |  |
| Rehearsal type | redeploy previous artifact / config rollback / approved tabletop |
| Operator |  |
| Start/end time |  |
| Health/readiness result |  |
| AdminApps no-fallback smoke result |  |
| Data rollback used | yes/no |
| Approval |  |
| Deviations |  |

Do not approve live controlled production until rollback has either been rehearsed on the target environment or formally accepted by the release owner with documented risk.
