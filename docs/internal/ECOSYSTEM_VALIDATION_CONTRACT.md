# Ecosystem Validation Contract

Fecha: 2026-06-29

## Objetivo

Definir los comandos oficiales y reproducibles para validar cada producto en su repositorio correcto, sin mezclar responsabilidades entre ISO Smart, MedSupplier y AdminApps.

Este contrato reemplaza como referencia viva a reportes historicos fechados. Los reportes historicos se conservan como evidencia, pero no deben usarse para introducir comandos cruzados.

## Principios obligatorios

1. MedSupplier se valida desde `/home/felipe/proyectos/ISO_Smart_MedSupplier`.
2. AdminApps se valida desde `/home/felipe/proyectos/adminapps`.
3. ISO Smart se valida desde `/home/felipe/proyectos/isosmart` como producto separado y benchmark tecnico.
4. Ningun comando oficial de MedSupplier debe depender del venv de ISO Smart.
5. Los resultados PASS/FAIL de ejecucion completa se registran en reportes de etapa, no se maquillan en este contrato.

## Entornos oficiales

| Producto | Area | Entorno oficial | Estado | Observacion |
| --- | --- | --- | --- | --- |
| MedSupplier | Backend | `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend/.venv312` | Presente | Python 3.12.13 detectado. |
| MedSupplier | Frontend | `/home/felipe/proyectos/ISO_Smart_MedSupplier/frontend/node_modules` con `package-lock.json` | Presente | Usar `npm ci` en CI y ambientes limpios; `npm install` aceptable en local. |
| AdminApps | Backend | `/home/felipe/proyectos/adminapps/backend/.venv312` | Presente | Python 3.12.13 detectado; preferido para validacion actual. |
| AdminApps | Backend legado | `/home/felipe/proyectos/adminapps/backend/venv_admin` | Presente | Python 3.9.25 detectado; legado documentado en README, no recomendado como contrato nuevo. |
| AdminApps | Frontend | `/home/felipe/proyectos/adminapps/frontend/node_modules` con `package-lock.json` | Presente | `package.json` actual incluye `lint` y `build`. |
| ISO Smart | Backend benchmark | `/home/felipe/proyectos/isosmart/backend/.venv312` | Presente | Python 3.12.13 detectado; no usar para validar MedSupplier. |
| ISO Smart | Frontend benchmark | `/home/felipe/proyectos/isosmart/frontend` | Presente | Producto separado. |

## Tabla oficial de validacion

| Producto | Repo | Area | Comando oficial | Estado | Observacion |
| --- | --- | --- | --- | --- | --- |
| MedSupplier | `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend` | Backend dependency setup | `python3.12 -m venv .venv312 && ./.venv312/bin/python -m pip install --upgrade pip && ./.venv312/bin/pip install -r requirements.txt -r requirements-dev.txt` | Oficial | Ejecutar solo cuando se reconstruye entorno. |
| MedSupplier | `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend` | Backend check | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check` | Oficial | Settings de test propios. |
| MedSupplier | `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend` | Migraciones check | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py makemigrations --check --dry-run` | Oficial | No usar `migrate --fake`. |
| MedSupplier | `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend` | Migrate plan | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py migrate --plan` | Oficial | Solo inspecciona plan. |
| MedSupplier | `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend` | Backend tests | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py test medsupplier` | Oficial | Cobertura focalizada MedSupplier. |
| MedSupplier | `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend` | AdminApps smoke | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e` | Oficial con observacion | La seguridad del fallback se endurece en ETAPA 5. |
| MedSupplier | `/home/felipe/proyectos/ISO_Smart_MedSupplier/frontend` | Frontend dependency setup | `npm ci` | Oficial CI | Usar `npm install` solo para desarrollo local cuando corresponda. |
| MedSupplier | `/home/felipe/proyectos/ISO_Smart_MedSupplier/frontend` | Frontend lint | `npm run lint` | Oficial | Script existe en `frontend/package.json`. |
| MedSupplier | `/home/felipe/proyectos/ISO_Smart_MedSupplier/frontend` | Frontend build | `npm run build` | Oficial | Build Vite. |
| MedSupplier | `/home/felipe/proyectos/ISO_Smart_MedSupplier/frontend` | E2E MedSupplier | `npm run test:e2e:medsupplier` | Oficial | Default corregido para usar venv propio de MedSupplier. |
| AdminApps | `/home/felipe/proyectos/adminapps/backend` | Backend dependency setup | `python3.12 -m venv .venv312 && ./.venv312/bin/python -m pip install --upgrade pip && ./.venv312/bin/pip install -r requirements.txt` | Oficial | README legado menciona `venv_admin`; contrato nuevo usa `.venv312`. |
| AdminApps | `/home/felipe/proyectos/adminapps/backend` | Backend check | `DJANGO_SETTINGS_MODULE=config.settings_test ./.venv312/bin/python manage.py check` | Oficial | Settings de test existen. |
| AdminApps | `/home/felipe/proyectos/adminapps/backend` | Migraciones check | `DJANGO_SETTINGS_MODULE=config.settings_test ./.venv312/bin/python manage.py makemigrations --check --dry-run` | Oficial | Brechas de migracion se corrigen en ETAPA 4. |
| AdminApps | `/home/felipe/proyectos/adminapps/backend` | Migrate plan | `DJANGO_SETTINGS_MODULE=config.settings_test ./.venv312/bin/python manage.py migrate --plan` | Oficial | Inspeccion de plan, sin aplicar migraciones. |
| AdminApps | `/home/felipe/proyectos/adminapps/backend` | Backend tests | `DJANGO_SETTINGS_MODULE=config.settings_test ./.venv312/bin/python manage.py test apps.products apps.billing apps.users apps.api` | Oficial | Suite focalizada products, billing, users y api. |
| AdminApps | `/home/felipe/proyectos/adminapps/frontend` | Frontend dependency setup | `npm ci` | Oficial CI | `package-lock.json` presente. |
| AdminApps | `/home/felipe/proyectos/adminapps/frontend` | Frontend lint | `npm run lint` | Oficial | Script existe en `frontend/package.json`. |
| AdminApps | `/home/felipe/proyectos/adminapps/frontend` | Frontend build | `npm run build` | Oficial | Build Vite. |
| ISO Smart | `/home/felipe/proyectos/isosmart/backend` | Backend benchmark check | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check` | Benchmark | Producto separado; no bloquea MedSupplier salvo dependencia documentada. |
| ISO Smart | `/home/felipe/proyectos/isosmart/backend` | Backend benchmark tests | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py test authentication.tests integration.tests core.tests` | Benchmark | Basado en workflows existentes de ISO Smart. |
| ISO Smart | `/home/felipe/proyectos/isosmart/backend` | Migraciones benchmark | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py makemigrations --check --dry-run` | Benchmark | No es contrato de MedSupplier. |
| ISO Smart | `/home/felipe/proyectos/isosmart/frontend` | Frontend benchmark lint | `npm run lint` | Benchmark | Script existe. |
| ISO Smart | `/home/felipe/proyectos/isosmart/frontend` | Frontend benchmark build | `npm run build` | Benchmark | Script existe. |
| ISO Smart | `/home/felipe/proyectos/isosmart/frontend` | E2E benchmark | `npm run test:e2e` | Benchmark | Script existe. |

## Comandos no oficiales o eliminados del contrato

| Comando/patron | Estado | Motivo |
| --- | --- | --- |
| `/home/felipe/proyectos/isosmart/backend/.venv312/bin/python` usado desde MedSupplier | Eliminado | Era una dependencia cruzada incorrecta. MedSupplier debe usar `backend/.venv312`. |
| `DJANGO_SETTINGS_MODULE=backend.settings_test /home/felipe/proyectos/isosmart/backend/.venv312/bin/python manage.py test medsupplier` | Eliminado | Reemplazado por `./.venv312/bin/python` desde el backend de MedSupplier. |
| AdminApps `venv_admin` como entorno nuevo recomendado | Deprecado | Existe localmente, pero el contrato actual usa Python 3.12 en `.venv312`. |
| Comandos de ISO Smart como validacion de MedSupplier | Eliminado | ISO Smart es benchmark y producto separado. |

## Dependencia temporal de venv externo

Estado actual: no debe existir dependencia contractual de MedSupplier hacia el venv de ISO Smart.

Accion realizada en ETAPA 1: se corrigieron los defaults de E2E que apuntaban al venv de ISO Smart:

| Archivo | Cambio |
| --- | --- |
| `frontend/playwright.config.cjs` | El webServer backend usa `../backend/.venv312/bin/python`. |
| `frontend/tests/e2e/medsupplier-demo-runtime.spec.js` | `PYTHON_BIN` por defecto usa `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend/.venv312/bin/python`. |
| `README.md` | Validacion local usa `./.venv312/bin/python`. |

Plan residual:

1. ETAPA 2 debe reconstruir/validar formalmente el entorno propio de MedSupplier.
2. ETAPA 3 debe ejecutar E2E real y confirmar que no hay referencias runtime al venv de ISO Smart.
3. ETAPA 5 debe endurecer fallback AdminApps para que no sea permisivo ni silencioso en produccion.

## Gate de aceptacion ETAPA 1

| Criterio | Estado | Evidencia |
| --- | --- | --- |
| Ningun comando de MedSupplier se ejecuta desde repo ISO Smart. | PASS | Tabla oficial usa `/home/felipe/proyectos/ISO_Smart_MedSupplier`; defaults E2E corregidos. |
| AdminApps tiene comandos propios. | PASS | Tabla AdminApps usa `/home/felipe/proyectos/adminapps`. |
| ISO Smart queda como benchmark o producto separado. | PASS | Tabla ISO Smart marcada como `Benchmark`. |
| Se documenta si existe dependencia temporal de venv externo. | PASS | Dependencia contractual eliminada; historial documentado. |
| Se define plan para eliminar venv cruzado. | PASS | Plan residual asignado a ETAPAS 2 y 3 para validacion completa. |

## Decision

Estado: aprobado con observaciones.

Decision: ETAPA 1 completada a nivel de contrato.

Observaciones:

1. La ejecucion completa de comandos queda para ETAPA 2 y posteriores.
2. AdminApps mantiene documentacion legacy ISO-centrica que debe corregirse en ETAPA 4.
3. El fallback AdminApps de MedSupplier sigue siendo una brecha a endurecer en ETAPA 5.
