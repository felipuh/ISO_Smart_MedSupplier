# Production-Like Hardening

Date: 2026-06-29

Scope: ISO Smart MedSupplier backend and AdminApps backend. This document records production-like readiness controls. It does not claim formal regulated production validation.

## Controls

### Runtime Settings

- `ENVIRONMENT=production` enables production guardrails.
- `DEBUG=False` is required in production.
- `SECRET_KEY` / `DJANGO_SECRET_KEY` must be provided by a secret manager or protected environment store.
- `ALLOWED_HOSTS` must be explicit for each deployed hostname.
- `ADMIN_APPS_ALLOW_LOCAL_FALLBACK=False` is required for MedSupplier production-like deployments.

### Browser And Transport Security

- Secure cookies are forced in production even if local `.env` values are stale:
  - `SESSION_COOKIE_SECURE=True`
  - `CSRF_COOKIE_SECURE=True`
- Cookies remain `HttpOnly` and `SameSite=Lax`.
- `SECURE_SSL_REDIRECT` defaults to `True` in production.
- `SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https')` is configured for reverse-proxy TLS termination.
- `SECURE_HSTS_SECONDS` defaults to `31536000` in production.
- `SECURE_HSTS_INCLUDE_SUBDOMAINS` defaults to `True` in production.
- `SECURE_HSTS_PRELOAD` remains opt-in and is intentionally not enabled by default.

### Security Headers

- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Cross-Origin-Opener-Policy: same-origin`
- `Content-Security-Policy: frame-ancestors 'none'`
- `Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()`

### CORS And CSRF

- `CORS_ALLOWED_ORIGINS` must list exact HTTPS origins.
- `CSRF_TRUSTED_ORIGINS` must list exact HTTPS origins.
- Wildcard origins are not part of the production-like contract.

### Rate Limiting

- DRF anonymous and authenticated throttles are enabled.
- Baseline rates:
  - `THROTTLE_ANON_RATE=60/minute`
  - `THROTTLE_USER_RATE=300/minute`
- Product-specific stricter throttles can be added in a later security pass.

### Logging

- Request IDs are propagated with `X-Request-ID`.
- Logs must not include API keys, JWTs, passwords, database credentials, or secret values.
- Stage 8 verification intentionally checks only env key names, not secret contents.

### Health And Readiness

- MedSupplier exposes public operational probes:
  - `GET /health`
  - `GET /ready`
  - `GET /api/health/`
  - `GET /api/ready/`
- Probes return minimal service/database status only.
- AdminApps integration health remains protected by integration API key where applicable.

## Check Deploy Result

Commands:

```bash
backend/.venv312/bin/python backend/manage.py check --deploy --settings=backend.settings
/home/felipe/proyectos/adminapps/backend/.venv312/bin/python manage.py check --deploy --settings=config.settings
```

Result on 2026-06-29:

- MedSupplier: PASS with one justified warning.
- AdminApps: PASS with one justified warning.

Justified warning:

- `security.W021`: `SECURE_HSTS_PRELOAD` is not `True`.
- Rationale: browser HSTS preload is a domain-level commitment. It should be enabled only after TLS, subdomains, rollback ownership, and preload submission policy are formally approved. This is not a blocker for production-like readiness.

## Residual Risks

- Binary PDF generation for evidence packages is not implemented.
- HSTS preload remains a deployment governance decision.
- Backup/restore commands must be rehearsed against staging data before customer-regulated use.
- This state is production-like and audit-ready, not a substitute for customer validation, SOPs, or formal regulated production approval.
