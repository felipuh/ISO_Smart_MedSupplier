# ISO Smart MedSupplier Remediation Release Notes

Fecha: 2026-06-26

## Brechas corregidas

- E2E MedSupplier aislado del backend equivocado en `127.0.0.1:8002`; Playwright ahora levanta el backend del workspace actual en `127.0.0.1:18002`.
- Seed demo idempotente endurecido para usuarios por rol, password funcional, usuarios activos, lockout reseteado y scopes MedSupplier explícitos.
- Suite E2E ampliada con smoke por roles Supplier Finance, Supplier Quality, Supplier Logistics, Supplier Viewer, Customer Buyer, Customer Quality, Customer Auditor y Customer Viewer.
- Datos demo ajustados para validar privacidad real: cuenta principal y quote compartidas con Customer; pipeline privado Supplier aislado.
- Guardrail backend agregado contra serializers inseguros y catálogo de campos privados comerciales.
- Smoke AdminApps agregado vía comando `check_medsupplier_adminapps`.
- Fallback local de módulos incluye `MEDSUPPLIER` sin abrir permisos globales.

## Comandos ejecutados y resultado

- `DJANGO_SETTINGS_MODULE=backend.settings_test /home/felipe/proyectos/isosmart/backend/.venv312/bin/python manage.py check`: PASS, 0 issues.
- `DJANGO_SETTINGS_MODULE=backend.settings_test /home/felipe/proyectos/isosmart/backend/.venv312/bin/python manage.py makemigrations --check --dry-run`: PASS, No changes detected.
- `DJANGO_SETTINGS_MODULE=backend.settings_test /home/felipe/proyectos/isosmart/backend/.venv312/bin/python manage.py migrate --plan`: PASS, No planned migration operations.
- `DJANGO_SETTINGS_MODULE=backend.settings_test /home/felipe/proyectos/isosmart/backend/.venv312/bin/python manage.py test medsupplier`: PASS, 26 tests OK.
- `/home/felipe/proyectos/isosmart/backend/.venv312/bin/python manage.py check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e`: PASS con fallback local controlado; AdminApps externo no disponible/404 para módulos, sin apertura de permisos globales.
- `npm run lint`: PASS.
- `npm run build`: PASS.
- `npm run test:e2e:medsupplier`: PASS, 5 tests OK.
- `/home/felipe/proyectos/isosmart/backend/.venv312/bin/python -m pip check`: FAIL operativo, `No module named pip`; no se instaló pip en el venv compartido.

## Riesgos restantes

- No apto para producción regulada sin hardening production-like, revisión humana formal y evidencia aprobada.
- Document Room y CAPAAction permanecen como MVP/control parcial; siguiente sprint debe profundizar versionado documental y acciones CAPA.
- PDF audit-ready real sigue pendiente si no se incorpora una librería/plantilla aprobada.

## Decisión recomendada

Aprobado para demo controlada si todos los comandos finales pasan. No declarar cumplimiento regulatorio completo.

## Próximo sprint

- CAPAAction con effectiveness check formal.
- Document Room major/minor, obsolescencia y revisión vigente con reglas completas.
- Export PDF audit-ready.
- Barrido exhaustivo por endpoint y rol en backend.
