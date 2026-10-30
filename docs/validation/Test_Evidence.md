# Test Evidence

Date: 2026-06-29

## MedSupplier Evidence

| Command | Result |
| --- | --- |
| `backend/.venv312/bin/python backend/manage.py check --settings=backend.settings_test` | PASS |
| `backend/.venv312/bin/python backend/manage.py makemigrations --check --dry-run --settings=backend.settings_test` | PASS, no changes detected |
| `backend/.venv312/bin/python backend/manage.py test core.tests.ProductionLikeProbeTests medsupplier --settings=backend.settings_test` | PASS, 48 tests |
| `cd frontend && npm run lint` | PASS |
| `cd frontend && npm run build` | PASS |
| `cd frontend && npm run test:e2e:medsupplier` | PASS, 5 tests |
| `backend/.venv312/bin/python backend/manage.py check --deploy --settings=backend.settings` | PASS with accepted `security.W021` |

## AdminApps Evidence

| Command | Result |
| --- | --- |
| `/home/felipe/proyectos/adminapps/backend/.venv312/bin/python manage.py check --settings=config.settings_test` | PASS |
| `/home/felipe/proyectos/adminapps/backend/.venv312/bin/python manage.py makemigrations --check --dry-run --settings=config.settings_test` | PASS, no changes detected |
| `/home/felipe/proyectos/adminapps/backend/.venv312/bin/python manage.py test apps.products apps.billing apps.users apps.api --settings=config.settings_test` | PASS, 123 tests |
| `cd /home/felipe/proyectos/adminapps/frontend && npm run lint` | PASS with existing warnings |
| `cd /home/felipe/proyectos/adminapps/frontend && npm run build` | PASS |
| `/home/felipe/proyectos/adminapps/backend/.venv312/bin/python manage.py check --deploy --settings=config.settings` | PASS with accepted `security.W021` |

## Evidence Interpretation

The package is validation-ready and audit-ready for human review. It requires formal validation execution and approval by the customer/company before regulated use.
