# Production-Like Hardening - 2026-06-27

## MedSupplier

Estado: listo para demo controlada con hardening parcial, no para produccion regulada completa.

- `DEBUG`: por defecto `False` en settings; production levanta error si queda activo.
- `ALLOWED_HOSTS`: configurable por env; incluye hosts Smart3AI/MedSupplier locales.
- Cookies: `SESSION_COOKIE_SECURE` y `CSRF_COOKIE_SECURE` dependen de env y default `not DEBUG`.
- CSRF: middleware activo; clase `CsrfExemptAPIMiddleware` documentada como deprecated/no-op.
- CORS: restringible por `CORS_ALLOWED_ORIGINS`; revisar origenes antes de prod.
- Headers: `SECURE_CONTENT_TYPE_NOSNIFF=True`, `X_FRAME_OPTIONS='DENY'`, referrer policy strict-origin-when-cross-origin.
- Rate limiting: DRF anon/user throttles configurados.
- Logging: request id y logging estructurado parcial.
- Audit trail: MedSupplier registra eventos de cambios y workflows.
- Secret management: `.env.example` existe; no usar secretos de ejemplo en ambientes reales.
- Health/readiness: pendiente formalizar endpoint sin autenticacion si se requiere para probes.
- `check --deploy`: pendiente ejecutar con env production-like validado.

## AdminApps

Estado: bloqueado para RC serio hasta limpiar baseline.

- `check` pasa con warning `staticfiles.W004`.
- `makemigrations --check` falla por cambio pendiente en `subscriptions.Plan.modules_included`.
- Tests 2FA fallan.
- Frontend no tiene script `lint`.
- Products/entitlements siguen parcialmente ISO-centric.

## Decision

Apto para demo controlada de MedSupplier con evidencia local. No apto para release candidate ecosistema hasta corregir AdminApps y validar contrato producto-neutral.
