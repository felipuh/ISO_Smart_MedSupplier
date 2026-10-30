# MedSupplier Pre-Pilot Validation Evidence

Date: 2026-06-29 16:02 CST

## Scope

Pre-pilot rerun for ISO Smart MedSupplier after closing the local-target AdminApps no-fallback smoke.

This evidence supports controlled demo, paid pilot, and controlled enterprise MVP readiness with restrictions. It does not approve live controlled production or full regulated production.

## Version

- Repository: `/home/felipe/proyectos/ISO_Smart_MedSupplier`
- Branch: `main`
- Base commit: `3907d0e`
- Worktree: controlled pending release/deploy/docs/AdminApps smoke hardening changes remain uncommitted.

## Backend Evidence

| Command | Result | Observation |
| --- | --- | --- |
| `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check` | PASS | No issues. |
| `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py makemigrations --check --dry-run` | PASS | No changes detected. |
| `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py migrate --plan` | PASS | No planned migration operations. |
| `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py test medsupplier` | PASS | 47 tests OK. |

Backend gate decision: PASS.

## Frontend Evidence

| Command | Result | Observation |
| --- | --- | --- |
| `npm run lint` | PASS | ESLint completed with exit 0. |
| `npm run build` | PASS | Vite production build completed. |
| `npm run test:e2e:medsupplier` | PASS | 5/5 Playwright tests passed. |

Frontend gate decision: PASS.

## E2E Evidence

Command:

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier/frontend
npm run test:e2e:medsupplier
```

Result:

```text
5 passed
```

Coverage observed:

- MedSupplier demo workspace supports data entry and explains blocked actions.
- Supplier Finance can access private cockpit and financial API fields.
- Supplier Quality and Logistics cannot access private financial cockpit.
- Supplier Viewer is read-only and backend rejects mutation.
- Customer roles are scoped, read filtered data, and never see private cockpit or financial fields.

E2E artifact note:

- Playwright `.last-run.json` exists under `frontend/test-results`.
- No failure artifact was produced because the suite passed.

## AdminApps Context

The local-target AdminApps no-fallback smoke passed before this pre-pilot rerun:

```bash
DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e --no-fallback
```

Result:

```text
product_access_source=adminapps
medsupplier_entitlement_enabled=True
medsupplier_access_reason=ok
MedSupplier AdminApps smoke passed.
```

Reference: `docs/release/ADMINAPPS_REAL_SMOKE_EVIDENCE.md`.

## Known Limitations

- Controlled production is still not approved.
- Final staging/production target must repeat no-fallback AdminApps smoke.
- SSL/domain verification remains pending for controlled production.
- Backup artifact/checksum remains pending for controlled production.
- Restore drill remains pending.
- Rollback rehearsal or formal acceptance remains pending.
- Monitoring activation remains pending.
- Human release approval remains pending.
- Full regulated production and formal validation remain not approved.
- Binary PDF evidence export remains backlog or buyer-specific scope.
- ISO Smart remains separate and is not included in this MedSupplier pre-pilot gate.

## Gate Decision

Pre-pilot validation status: PASS.

Approved level supported by this evidence:

- Controlled demo: GO.
- Paid pilot: GO WITH RESTRICTIONS.
- Controlled enterprise MVP: GO WITH RESTRICTIONS.

Not approved:

- Live controlled production.
- Full regulated production.
- Unrestricted ecosystem Release Candidate.

## Required Next Step

Proceed to Stage 4 target production-control gates, keeping status:

```text
Controlled production: NOT APPROVED YET
```
