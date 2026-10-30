# QA Evidence - ISO Smart MedSupplier

Fecha de ejecucion principal: 2026-07-02 America/Costa_Rica.

## Backend

- Python backend validado: Python 3.9 en `backend/.venv`.
- `.venv/bin/pip install -r requirements.txt`: OK, incluyendo `pysqlite3-binary==0.5.4` y `chromadb==1.3.5`.
- `.venv/bin/python manage.py check`: OK.
- `.venv/bin/python manage.py check --deploy --settings=backend.settings_test`: OK con warnings esperados de entorno test/local.
- `DJANGO_ENV=production ... .venv/bin/python manage.py check --deploy`: OK, sin issues, usando overrides productivos completos de prueba.
- `.venv/bin/python manage.py makemigrations --check --dry-run`: OK, sin cambios detectados.
- `.venv/bin/python manage.py test medsupplier.tests_security_guardrails medsupplier.tests.MedSupplierSerializerGuardrailTests --settings=backend.settings_test`: OK, 3 tests.
- `.venv/bin/python manage.py test --settings=backend.settings_test`: OK, 135 tests.
- `rg "fields\\s*=\\s*['\\\"]__all__['\\\"]" backend --glob '!**/migrations/**' --glob '!**/staticfiles/**'`: sin resultados.
- `.venv/bin/python manage.py showmigrations --plan --settings=backend.settings_test`: ejecutado; migraciones mostradas como aplicadas.

## Frontend

- `npm ci`: OK, 0 vulnerabilidades reportadas.
- `npm run lint`: OK. Nota Babel: `src/i18n/messages.js` supera 500 KB.
- `npm run build`: OK.
- `frontend/src/services/api.js` usa `VITE_API_BASE_URL || "/api"`.
- `frontend/.env.example` agregado con `VITE_LOCAL_AUTH_BYPASS=0`.
- El boton de demo local queda condicionado a `VITE_LOCAL_AUTH_BYPASS=1`.

Build generado:

- `dist/index.html`
- bundles principales de MedSupplier, vendors, settings e i18n.

## Observaciones

- La suite completa paso despues de ajustar el mock del vector store en `integration.tests.AssistantApiTests`.
