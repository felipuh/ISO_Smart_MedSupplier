# MedSupplier Release Freeze Recommendation

Date: 2026-06-29 15:39 CST

## Scope

This recommendation covers the post-acceptance freeze review for ISO Smart MedSupplier after the Final Enterprise Acceptance Report decision: GO WITH RESTRICTIONS.

The objective is to keep MedSupplier controlled for demo, paid pilot, and controlled enterprise MVP preparation without declaring controlled production or regulated production.

## Git Status Reviewed

Command:

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier
git status --short
git diff --stat
git diff --check
```

Result:

- `git diff --check`: PASS, no whitespace or conflict-marker errors reported.
- Pending changes are release, deploy, documentation, and AdminApps smoke hardening changes.

## Pending Files

Release/deploy files already identified in the Final Enterprise Acceptance Report:

- `deploy/nginx/medsupplier.conf`
- `deploy/systemd/medsupplier-backend.service`
- `docs/deploy/MONITORING_LOGGING_RUNBOOK.md`
- `docs/deploy/TENANT_OPERATIONS_RUNBOOK.md`
- `docs/release/CONTROLLED_PRODUCTION_READINESS_REPORT.md`
- `docs/release/FINAL_ENTERPRISE_ACCEPTANCE_REPORT.md`
- `docs/release/REGULATED_PRODUCTION_ROADMAP.md`
- `docs/release/RELEASE_CANDIDATE_REPORT.md`

Additional post-acceptance sprint files:

- `backend/integration/client.py`
- `backend/medsupplier/management/commands/check_medsupplier_adminapps.py`
- `backend/medsupplier/tests.py`
- `docs/release/MEDSUPPLIER_RELEASE_FREEZE_RECOMMENDATION.md`
- `docs/release/ADMINAPPS_REAL_SMOKE_EVIDENCE.md`

## Release Changes Identified

- Nginx `/health` and `/ready` now proxy to the MedSupplier backend instead of returning static health text.
- systemd now points Gunicorn to the MedSupplier backend virtual environment.
- AdminApps client now accepts an explicit per-call local fallback policy for product validation and sends configurable forwarded-proto headers for proxy-aligned integration smoke.
- AdminApps smoke command now supports `--no-fallback` for target/staging/production evidence.
- Tests verify that `--no-fallback` passes with direct AdminApps access and rejects local fallback.
- Local AdminApps target migrations were applied and local demo organization mapping was seeded to close the no-fallback smoke.

## Risks

| Risk | Severity | Action |
| --- | --- | --- |
| Real AdminApps target smoke must be repeated in final staging/production target. | Medium | Local target no-fallback smoke now passes; repeat before controlled production approval. |
| Release files are uncommitted. | Medium | Commit only reviewed release/deploy/docs/smoke-hardening changes after human approval. |
| Controlled production target gates remain pending. | High | Complete SSL/domain, backup/checksum, restore drill, rollback rehearsal, monitoring activation, real AdminApps smoke, and human approval. |
| ISO Smart frontend lint/E2E remain outside this MedSupplier freeze. | Medium | Keep ISO Smart separate unless remediated for joint sale. |

## Recommendation

Recommended human decision: approve a scoped release commit for MedSupplier pilot readiness only after reviewing the pending diff.

Suggested branch:

```bash
git switch -c release/medsupplier-post-acceptance-pilot-2026-06-29
```

Suggested commit:

```bash
git add deploy/nginx/medsupplier.conf \
  deploy/systemd/medsupplier-backend.service \
  docs/deploy/MONITORING_LOGGING_RUNBOOK.md \
  docs/deploy/TENANT_OPERATIONS_RUNBOOK.md \
  docs/release/CONTROLLED_PRODUCTION_READINESS_REPORT.md \
  docs/release/FINAL_ENTERPRISE_ACCEPTANCE_REPORT.md \
  docs/release/REGULATED_PRODUCTION_ROADMAP.md \
  docs/release/RELEASE_CANDIDATE_REPORT.md \
  backend/integration/client.py \
  backend/medsupplier/management/commands/check_medsupplier_adminapps.py \
  backend/medsupplier/tests.py \
  docs/release/MEDSUPPLIER_RELEASE_FREEZE_RECOMMENDATION.md \
  docs/release/ADMINAPPS_REAL_SMOKE_EVIDENCE.md
git commit -m "Harden MedSupplier pilot release evidence"
```

Suggested tag after human review and remaining pre-pilot gates pass:

```bash
git tag medsupplier-pilot-2026-06-29-rc1
```

Do not tag as production-ready while final target production-control gates are still open.

## Required Human Approval

Approval is required from:

- Release owner
- Product owner
- Security or DevOps owner

Decision options:

- Approve commit for paid pilot preparation.
- Hold commit until final staging/production target smoke is repeated, if release owner requires it before branch/tag.
- Split code hardening and documentation into separate commits.

## Decision

Release freeze status: CONTROLLED CHANGES IDENTIFIED.

Commit/tag status: HUMAN APPROVAL REQUIRED.

Production status: NOT APPROVED.

AdminApps no-fallback smoke status: PASS for local target; repeat required in final staging/production target.
