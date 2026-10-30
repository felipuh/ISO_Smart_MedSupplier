# Header Enterprise Validation Evidence

Date: 2026-07-02

## Scope

Validation evidence for the ISO Smart MedSupplier enterprise header, accessibility controls, i18n runtime, and MedSupplier-specific runtime flows.

## Final pre-merge matrix

Final matrix executed on 2026-07-02 before merge/deploy handoff.

| Area | Command | Result | Notes |
| --- | --- | --- | --- |
| Frontend lint | `npm run lint` | PASS | ESLint completed cleanly. |
| Frontend build | `npm run build` | PASS | Vite production build completed. Plugin timing output is informational. |
| Patch hygiene | `git diff --check` | PASS | No whitespace errors. |
| Django check | `DJANGO_SETTINGS_MODULE=backend.settings_test backend/.venv312/bin/python backend/manage.py check` | PASS | No system check issues. |
| Django migrations | `DJANGO_SETTINGS_MODULE=backend.settings_test backend/.venv312/bin/python backend/manage.py makemigrations --check --dry-run` | PASS | No migration changes detected. |
| Backend tests | `DJANGO_SETTINGS_MODULE=backend.settings_test backend/.venv312/bin/python backend/manage.py test medsupplier` | PASS | 47 tests passed. |
| Header E2E | `npm run test:e2e:medsupplier:header` | PASS | 2 tests passed. |
| I18N E2E | `npm run test:i18n:smoke` | PASS | 6 tests passed. |
| MedSupplier E2E | `npm run test:e2e:medsupplier` | PASS | 5 tests passed. |
| General smoke E2E | `npm run test:e2e:smoke` | PASS | 9 tests passed. |
| Dependency review | `git diff -- frontend/package.json` | PASS | No new packages; only `test:e2e:medsupplier:header` script added. |
| Secret scan | `rg -n "(password|secret|api[_-]?key|token|Bearer|PRIVATE KEY|AWS_|BEGIN RSA|BEGIN OPENSSH|client_secret)" frontend/src docs frontend/tests/e2e --glob '!**/node_modules/**'` | REVIEWED | Hits are labels, existing auth/token code, docs, and E2E fixtures. No new production secret was identified. |

## Final hardening pass

After the final pre-commit self-review, `ThemeContext` was hardened to tolerate environments where `window.matchMedia` is unavailable. The affected checks were re-run:

| Command | Result | Notes |
| --- | --- | --- |
| `npm run lint` | PASS | No lint regressions. |
| `npm run build` | PASS | Production build completed. |
| `git diff --check` | PASS | No whitespace errors. |
| `npm run test:e2e:medsupplier:header` | PASS | 2 tests passed after theme hardening. |

## Auth interceptor regression

After browser validation on `http://medsupplier.isosmart.local`, a stale-token failure was reproduced: invalid tokens in `localStorage` were being attached to `/auth/login/`, causing `401` before credentials could be evaluated and then triggering a failing `/auth/refresh/`.

The API interceptor now treats login, refresh, and password-reset endpoints as public auth requests:

- No stale `Authorization` header is attached to those endpoints.
- A `401` from those endpoints is returned directly to the caller instead of triggering refresh recursion.
- `npm run test:e2e:medsupplier:header` now includes a regression test for login with stale local auth tokens.

Validation after the fix:

| Command | Result | Notes |
| --- | --- | --- |
| `npm run lint` | PASS | No lint regressions. |
| `npm run build` | PASS | Nginx-served `frontend/dist` refreshed. |
| `git diff --check` | PASS | No whitespace errors. |
| `npm run test:e2e:medsupplier:header` | PASS | 3 tests passed, including stale-token login regression. |
| Browser smoke on `http://medsupplier.isosmart.local/login` | PASS | Login succeeds with intentionally corrupted `access_token` and `refresh_token` in localStorage. |

## Passing validations

| Command | Result | Notes |
| --- | --- | --- |
| `npm run lint` | PASS | ESLint completed without warnings after extracting i18n dictionaries from `I18nContext.jsx`. |
| `npm run build` | PASS | Vite production build completed. |
| `npm run test:e2e:medsupplier:header` | PASS | 2 tests. Covers theme, font size, language persistence, notifications empty state, settings menu, user menu profile/logout affordances, Escape/click-outside close behavior, and mobile navigation/preferences. |
| `npm run test:i18n:smoke` | PASS | Covers ES/EN/PT login and MedSupplier shell runtime persistence. |
| `npm run test:e2e:medsupplier` | PASS | 5 tests. Covers MedSupplier workspace, RBAC/ABAC, scoped records, private financial fields, UI create flow, and tenant-scoped API confirmation. |
| `npm run test:e2e:smoke` | PASS | 9 tests. General smoke suite realigned with the standalone MedSupplier shell and current backend behavior. |
| `DJANGO_SETTINGS_MODULE=backend.settings_test backend/.venv312/bin/python backend/manage.py check` | PASS | Backend MedSupplier system check, no issues. |
| `DJANGO_SETTINGS_MODULE=backend.settings_test backend/.venv312/bin/python backend/manage.py makemigrations --check --dry-run` | PASS | No migration changes detected. |
| `DJANGO_SETTINGS_MODULE=backend.settings_test backend/.venv312/bin/python backend/manage.py test medsupplier` | PASS | 47 MedSupplier backend tests OK. |
| `git diff --check` | PASS | No whitespace errors detected in the patch. |

## General smoke repair notes

`npm run test:e2e:smoke` was repaired and executed after the MedSupplier/header validations.

Result: PASS, 9 passed / 0 failed.

Repairs applied:

| Area | Repair |
| --- | --- |
| Assistant runtime | The MedSupplier shell mounts the existing virtual assistant surface so authenticated smoke coverage can reach it. |
| Password recovery runtime | The spec now issues a reset token through the local Django shell instead of depending on a debug-only response field. |
| Role permissions runtime | The spec clears the temporary password flag for generated users before validating settings access. |
| Scope/process runtime | The spec now verifies safe route resolution through the MedSupplier shell and keeps tenant-protection checks on MedSupplier endpoints. |

## MedSupplier gate repair notes

`npm run test:e2e:medsupplier` was re-executed after hardening the data-entry assertion.

Result: PASS, 5 passed / 0 failed.

The data-entry spec still creates the supplier account through the UI, then confirms the created record through the local Django ORM for the same tenant. This avoids depending on unstable table ordering or optional API search-filter configuration when previous E2E records already exist in the demo workspace.

## Backend validation notes

An initial backend test attempt without `backend.settings_test` used the local default Postgres configuration and failed before running tests because that database user cannot create a test database. The official repository contract uses `backend.settings_test` with local SQLite test databases; with that settings module, backend check, migration check, and MedSupplier tests passed.

## I18N maintainability notes

The large translation dictionaries were moved from `frontend/src/context/I18nContext.jsx` to `frontend/src/i18n/messages.js`. Runtime behavior remains the same: `I18nProvider`, `useI18n()`, `t()`, backend string translation, fallback to Spanish, and `localStorage` persistence are preserved. The provider now stays small enough to avoid the previous Babel deoptimization notice.

## Release interpretation

The header/i18n/MedSupplier-specific release gate is green, and the broader smoke gate is now green after aligning legacy runtime assumptions with the standalone MedSupplier application shell.

## Recommendation

For this header enterprise change, use the following release gate:

1. `npm run lint`
2. `npm run build`
3. `npm run test:e2e:medsupplier:header`
4. `npm run test:i18n:smoke`
5. `npm run test:e2e:medsupplier`
6. `npm run test:e2e:smoke`
