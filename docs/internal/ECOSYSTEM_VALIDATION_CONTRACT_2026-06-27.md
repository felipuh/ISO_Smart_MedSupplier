# Ecosystem Validation Contract - 2026-06-27

| Producto | Area | Comando | Repo correcto | Estado | Observacion |
| -------- | ---- | ------- | ------------- | ------ | ----------- |
| MedSupplier | Backend check | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check` | `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend` | Pasa | Venv propio validado. |
| MedSupplier | Migraciones check | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py makemigrations --check --dry-run` | `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend` | Pasa | No changes detected. |
| MedSupplier | Migrate plan | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py migrate --plan` | `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend` | Pasa | No planned migration operations. |
| MedSupplier | Tests backend | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py test medsupplier` | `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend` | Pasa | 26 tests OK. |
| MedSupplier | AdminApps smoke | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e` | `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend` | Pasa | Requiere seed demo; pasa con fallback local controlado cuando AdminApps devuelve 404. |
| MedSupplier | Frontend lint | `npm run lint` | `/home/felipe/proyectos/ISO_Smart_MedSupplier/frontend` | Pasa | ESLint OK. |
| MedSupplier | Frontend build | `npm run build` | `/home/felipe/proyectos/ISO_Smart_MedSupplier/frontend` | Pasa | Build Vite OK. |
| MedSupplier | E2E | `npm run test:e2e:medsupplier` | `/home/felipe/proyectos/ISO_Smart_MedSupplier/frontend` | Pasa | 5 tests OK; valida login, supplier/customer, cockpit privado, read-only y filtros. |
| AdminApps | Backend check | `DJANGO_SETTINGS_MODULE=config.settings_test python manage.py check` | `/home/felipe/proyectos/adminapps/backend` | Pasa con warning | `staticfiles.W004`: falta `backend/static`. |
| AdminApps | Migraciones check | `DJANGO_SETTINGS_MODULE=config.settings_test python manage.py makemigrations --check --dry-run` | `/home/felipe/proyectos/adminapps/backend` | Falla | Requiere migracion `subscriptions/0002_alter_plan_modules_included.py`. |
| AdminApps | Migrate plan | `DJANGO_SETTINGS_MODULE=config.settings_test python manage.py migrate --plan` | `/home/felipe/proyectos/adminapps/backend` | Pendiente | Hay operaciones pendientes de billing, integration, token_blacklist y users. |
| AdminApps | Tests backend | `python manage.py test apps.products apps.billing apps.users apps.api` | `/home/felipe/proyectos/adminapps/backend` | Falla | 115 tests: 1 failure y 7 errors en 2FA login/rate-limit. |
| AdminApps | Frontend build | `npm run build` | `/home/felipe/proyectos/adminapps/frontend` | Pasa | Build Vite OK. |
| AdminApps | Frontend lint | `npm run lint` | `/home/felipe/proyectos/adminapps/frontend` | No definido | `package.json` no tiene script `lint`. |
| Iso Smart | Benchmark | `find/settings/docs review` | `/home/felipe/proyectos/isosmart` | Solo referencia | No se valida como parte contractual de MedSupplier. |
