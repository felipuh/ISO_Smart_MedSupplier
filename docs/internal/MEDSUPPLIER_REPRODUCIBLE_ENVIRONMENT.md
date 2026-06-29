# MedSupplier Reproducible Environment

Fecha: 2026-06-29

## Objetivo

Validar que MedSupplier puede instalarse y verificarse con entornos propios de backend y frontend, sin dependencia contractual del venv de ISO Smart.

## Entornos validados

| Area | Ruta | Estado | Evidencia |
| --- | --- | --- | --- |
| Backend Python | `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend/.venv312` | PASS | Python 3.12.13, dependencias instaladas, `pip check` sin conflictos. |
| Backend requirements | `backend/requirements.txt`, `backend/requirements-dev.txt` | PASS | Instalacion idempotente con pip. |
| Backend env example | `backend/.env.example` | PASS | Archivo producto MedSupplier, sin secretos reales. |
| Frontend Node | `/home/felipe/proyectos/ISO_Smart_MedSupplier/frontend` | PASS | `npm ci` completo con `package-lock.json`. |
| Frontend README | `frontend/README.md` | PASS | Documenta comandos propios y E2E con venv MedSupplier. |

## Comandos ejecutados

| Area | Comando | Resultado | Observacion |
| --- | --- | --- | --- |
| Backend | `./.venv312/bin/python -m pip install --upgrade pip` | PASS | Pip ya estaba actualizado. |
| Backend | `./.venv312/bin/pip install -r requirements.txt -r requirements-dev.txt` | PASS | Dependencias ya satisfechas. |
| Backend | `./.venv312/bin/python -m pip check` | PASS | `No broken requirements found.` |
| Backend | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check` | PASS | `System check identified no issues`. |
| Backend | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py makemigrations --check --dry-run` | PASS | `No changes detected`. |
| Backend | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py migrate --plan` | PASS | `No planned migration operations`. |
| Backend | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py test medsupplier` | PASS | 26 tests OK. |
| Frontend | `npm ci` | PASS | 310 packages installed, 0 vulnerabilities. |
| Frontend | `npm run lint` | PASS | ESLint completed without errors. |
| Frontend | `npm run build` | PASS | Vite build completed. |

## E2E venv dependency check

Active E2E defaults now point to MedSupplier:

| Archivo | Estado |
| --- | --- |
| `frontend/playwright.config.cjs` | Uses `../backend/.venv312/bin/python`. |
| `frontend/tests/e2e/medsupplier-demo-runtime.spec.js` | Uses `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend/.venv312/bin/python` unless `PYTHON_BIN` overrides it. |

Remaining documented references to `/home/felipe/proyectos/isosmart/backend/.venv312` are historical or benchmark-only and are not part of the official runtime contract.

## Gate de aceptacion

| Criterio | Estado | Evidencia |
| --- | --- | --- |
| MedSupplier backend corre con su propio entorno. | PASS | Backend checks/tests pass using `backend/.venv312`. |
| MedSupplier frontend corre en su propio workspace. | PASS | `npm ci`, lint and build pass in `frontend`. |
| No depende oficialmente del venv de ISO Smart. | PASS | Runtime defaults corrected; contract forbids venv cruzado. |
| Tests backend pasan. | PASS | 26 tests OK. |
| Lint frontend pasa. | PASS | `npm run lint` PASS. |
| Build frontend pasa. | PASS | `npm run build` PASS. |

## Decision

Estado: aprobado.

Decision: ETAPA 2 completada.

Se puede avanzar a ETAPA 3: si.

Observacion: E2E completo no se ejecuto en ETAPA 2 porque pertenece al gate de ETAPA 3; el setup ahora esta listo para ejecutarlo con venv propio.
