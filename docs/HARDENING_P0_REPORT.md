# Hardening P0/P1 Report - ISO Smart MedSupplier

Fecha de ejecucion principal: 2026-07-02 America/Costa_Rica.
Reporte actualizado: 2026-07-03.
Branch revisado: `hardening/p0-enterprise-readiness-20260702`.

## Alcance

- Backend Django en `backend/`.
- Frontend Vite en `frontend/`.
- No se modificaron archivos `.env` reales.
- No se ejecuto `sudo`.
- No se realizaron commits desde esta documentacion.

## Cambios aplicados

- `DJANGO_ENV` queda como variable canonica, con compatibilidad de lectura para `ENVIRONMENT`.
- Hosts locales y bypass de autenticacion local solo se habilitan en entorno de desarrollo.
- `ALLOW_LOCAL_AUTH_BYPASS_FOR_TESTS` requiere desarrollo y flag explicito.
- `.env.example` documenta `DJANGO_ENV` en ejemplos de desarrollo y produccion.
- Se reemplazaron `ModelSerializer.fields = "__all__"` por campos explicitos en serializers de `core`, `integration` y `performance`.
- Se agrego guardrail de seguridad para deshabilitar bypass local en produccion.
- Se corrigio el test de streaming del asistente para mockear el vector store sin requerir cargar Chroma durante la prueba.
- Se declararon `pysqlite3-binary` y `chromadb` en `backend/requirements.txt`, alineando dependencias con `integration/services/vector_store.py`.
- El frontend ahora documenta `VITE_API_BASE_URL=/api` y `VITE_LOCAL_AUTH_BYPASS=0` en `frontend/.env.example`.
- El cliente API frontend usa `VITE_API_BASE_URL` con fallback seguro a `/api`.
- El boton de credenciales demo locales solo se muestra si `VITE_LOCAL_AUTH_BYPASS=1` y el host es local.

## Estado

Resultado: implementacion P0/P1 validada para ISO Smart MedSupplier.

Nota operativa: el frontend compila correctamente. Durante lint se registro una nota Babel por `src/i18n/messages.js` mayor a 500 KB; no fallo el comando.
