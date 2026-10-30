# Production Hardening Checklist

Fecha: 2026-06-26

Estado: checklist operativo para readiness production-like. No implica cumplimiento regulatorio completo.

- `DEBUG=False` en producción.
- `ALLOWED_HOSTS` limitado a dominios aprobados.
- `CORS_ALLOWED_ORIGINS` y `CSRF_TRUSTED_ORIGINS` explícitos.
- `SESSION_COOKIE_SECURE=True` y `CSRF_COOKIE_SECURE=True` bajo HTTPS.
- `SECURE_SSL_REDIRECT=True` detrás de proxy correctamente configurado.
- `SECURE_HSTS_SECONDS` habilitado tras validar HTTPS end-to-end.
- `SECURE_CONTENT_TYPE_NOSNIFF=True`.
- `SECURE_REFERRER_POLICY` definido.
- `X_FRAME_OPTIONS='DENY'` o excepción documentada.
- JWT access/refresh con expiración revisada para demo y producción.
- DRF throttling habilitado para auth y endpoints sensibles.
- Logs de seguridad sin secretos, tokens ni passwords.
- Secretos exclusivamente por variables de entorno o secret manager.
- AdminApps identity source requerido en producción; fallback local solo para pruebas/control operativo documentado.
