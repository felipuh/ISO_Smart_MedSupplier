# ISO Smart Joint Sale Readiness Note

Date: 2026-06-30

## Decision

ISO Smart frontend benchmark remediation is complete for the audited blockers.

Status:
- ISO Smart standalone technical gate: PASS for benchmark use.
- ISO Smart inclusion in a joint ecosystem release: PASS for frontend lint/build/E2E benchmark evidence, subject to the same target-environment and human approval gates that apply to the ecosystem.

This note does not approve regulated production or customer production use by itself.

## Remediated P1 Items

1. Frontend lint failures:
   - Removed unused i18n bindings from `OnboardingGuard.jsx`, `FontSizeContext.jsx`, and `ThemeContext.jsx`.
   - Declared the `process` global in `vite.config.js`.
   - Result: `npm run lint` PASS.

2. Password recovery E2E failure:
   - Enabled local/test-only debug recovery through explicit `X-Debug-Recovery` or `debug_recovery=1`.
   - Restricted debug recovery to `DEBUG` or local auth bypass test settings.
   - Parameterized backend URL in the E2E spec.
   - Result: password recovery E2E PASS.

3. Role permission E2E failures:
   - Rotated temporary passwords for generated role users before UI permission checks.
   - Prepared the test tenant with completed onboarding.
   - Stabilized test backend/proxy configuration through `BACKEND_URL` and `VITE_BACKEND_PROXY_TARGET`.
   - Result: role permission E2E PASS.

## Evidence

Commands executed from the ISO Smart worktree:

```bash
DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check
DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py makemigrations --check --dry-run
DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py test authentication.tests integration.tests core.tests
cd frontend && npm run lint
cd frontend && npm run build
cd frontend && BACKEND_URL=http://127.0.0.1:8012 VITE_BACKEND_PROXY_TARGET=http://127.0.0.1:8012 npm run test:e2e
```

Results:
- Backend check: PASS.
- Migration drift check: PASS, no changes detected.
- Backend benchmark tests: PASS, 78 tests OK.
- Frontend lint: PASS.
- Frontend build: PASS.
- Frontend E2E: PASS, 16/16.

## Notes

- The E2E benchmark used a local `backend.settings_test` backend on port `8012` to avoid interference from long-running hardened gunicorn processes on `8001/8002`.
- E2E specs now support `BACKEND_URL` and Vite supports `VITE_BACKEND_PROXY_TARGET` for reproducible test routing.
- `backend/test_default.sqlite3` was modified as local test state during the benchmark run and is not release code.

## Remaining Restrictions

ISO Smart is no longer blocking the joint frontend benchmark gate.

Still not approved by this note:
- Live controlled production.
- Full regulated production.
- Formal validation claims.
- Target-environment SSL/domain, backup, restore, rollback, monitoring, and human approval gates.
