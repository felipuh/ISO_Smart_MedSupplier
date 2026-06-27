# Test Plan

Run backend unit tests for MedSupplier privacy, permissions, workflows, audit, e-signature, FMEA, and evidence package behavior. Run frontend lint/build and MedSupplier E2E where the local browser/backend environment is available.

Required commands:
- `DJANGO_SETTINGS_MODULE=backend.settings_test /home/felipe/proyectos/isosmart/backend/.venv312/bin/python manage.py test medsupplier`
- `npm run lint`
- `npm run build`
- `npm run test:e2e:medsupplier`
