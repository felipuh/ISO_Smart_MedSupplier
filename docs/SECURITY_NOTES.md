# Security Notes - ISO Smart MedSupplier

## Configuracion

- Produccion debe definir `DJANGO_ENV=production`.
- No confiar en `ENVIRONMENT` para nuevos despliegues; queda solo como compatibilidad.
- Los alias locales (`127.0.0.1`, `localhost`, `testserver`) no se agregan automaticamente en produccion.
- `ALLOW_LOCAL_AUTH_BYPASS_FOR_TESTS=True` solo tiene efecto en desarrollo.
- `SECURE_SSL_REDIRECT`, HSTS y cookies seguras ya quedan controlados por entorno y fueron validados con `check --deploy`.
- `frontend/.env.example` deja `VITE_LOCAL_AUTH_BYPASS=0` por defecto.
- El boton de demo local depende de `VITE_LOCAL_AUTH_BYPASS=1`, ademas de host local.
- `VITE_API_BASE_URL` permite configurar el backend en frontend sin hardcodear dominios.

## Serializacion

- Los serializers revisados ya no usan `fields = "__all__"`.
- El guardrail `backend/medsupplier/tests_security_guardrails.py` debe mantenerse en CI.

## Integracion IA/RAG

- `integration/services/vector_store.py` depende de Chroma y pysqlite3; ambas dependencias quedaron declaradas en `backend/requirements.txt`.
- El test de streaming usa un modulo falso para aislar persistencia/conversacion de la disponibilidad de Chroma.

## Pendientes recomendados

- Vigilar tamano de `frontend/src/i18n/messages.js`; Babel ya reporta deoptimizacion de estilo por superar 500 KB.
- Ejecutar validacion con variables finales de deploy y servicios externos reales antes de produccion.
- Migrar almacenamiento de JWT en `localStorage` hacia cookies HttpOnly/SameSite en una fase coordinada backend/frontend.
