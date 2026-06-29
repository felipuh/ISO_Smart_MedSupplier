# ISO Smart MedSupplier Backend

Backend Django/DRF propio de ISO Smart MedSupplier.

## Entorno local reproducible

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier/backend
python3.12 -m venv .venv312
./.venv312/bin/python -m pip install --upgrade pip
./.venv312/bin/pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
```

## Contrato de validacion

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier/backend
DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check
DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py makemigrations --check --dry-run
DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py migrate --plan
DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py test medsupplier
DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e
```

El smoke AdminApps requiere que exista la organizacion demo y que tenga entitlement `MEDSUPPLIER` mas scopes locales activos. Para QA local, `npm run test:e2e:medsupplier` ejecuta el seed demo antes del flujo Playwright.

## Regla de arquitectura

MedSupplier es producto independiente. Este backend no debe depender contractualmente del venv de `/home/felipe/proyectos/isosmart`; el contrato oficial usa siempre `backend/.venv312`.
