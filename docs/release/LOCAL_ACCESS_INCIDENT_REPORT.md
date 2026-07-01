# Local Access Incident Report

Date: 2026-06-30

## Summary

Local browser login failed with `AxiosError: Network Error` because the browser requested:

```text
https://medsupplier.isosmart.local/api/auth/login/
```

The local replica currently has Nginx listening only on HTTP port 80. There is no active local HTTPS listener on port 443 and no local SSL certificate installed yet.

## Root Causes Confirmed

1. `medsupplier.isosmart.local` resolved to `127.0.0.1`, but port 443 was not listening.
2. MedSupplier had production-like HTTPS redirect enabled before the runtime fix.
3. The process bound to `127.0.0.1:8002` initially appeared ambiguous in `ps` output because the displayed interpreter path referenced the ISO Smart virtualenv path. The active process was verified through `/proc/<pid>/cwd` and now points to the MedSupplier backend directory.
4. `isosmart.local` and `adminapps.isosmart.local` were not present in `/etc/hosts`, so those hostnames did not resolve in the browser.

## Remediation Applied

- MedSupplier runtime restarted on `127.0.0.1:8002` from:

```text
/home/felipe/proyectos/ISO_Smart_MedSupplier/backend
```

- The active MedSupplier Gunicorn process working directory was verified through `/proc/<pid>/cwd`.

- AdminApps runtime restarted on `127.0.0.1:8000` from:

```text
/home/felipe/proyectos/adminapps/backend
```

- MedSupplier and AdminApps settings now allow `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` to be controlled by environment variables while preserving secure production defaults.
- Local `.env` runtime flags are set to:

```text
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

## Validation Evidence

Commands executed:

```bash
DJANGO_SETTINGS_MODULE=backend.settings ./.venv312/bin/python manage.py check
DJANGO_SETTINGS_MODULE=config.settings BILLING_SCHEDULER_ENABLED=false ./.venv312/bin/python manage.py check
npm run lint
curl http://medsupplier.isosmart.local/
curl -X OPTIONS http://medsupplier.isosmart.local/api/auth/login/
curl --resolve adminapps.isosmart.local:80:127.0.0.1 http://adminapps.isosmart.local/
curl --resolve isosmart.local:80:127.0.0.1 http://isosmart.local/
```

Results:

| Check | Result |
| --- | --- |
| MedSupplier backend check | PASS |
| AdminApps backend check | PASS |
| MedSupplier frontend lint | PASS |
| MedSupplier HTTP root | 200 |
| MedSupplier login route OPTIONS | 200 |
| MedSupplier demo login | 200, JWT access and refresh returned |
| MedSupplier `/api/auth/me/` with JWT | 200 |
| AdminApps HTTP root with forced hostname resolution | 200 |
| ISO Smart HTTP root with forced hostname resolution | 200 |

## Required Local Host Fix

The current user cannot write `/etc/hosts`. A user with sudo privileges must add:

```text
127.0.0.1 medsupplier.isosmart.local medsupplier.smart3ai.local
127.0.0.1 isosmart.local isosmart.smart3ai.local smart3ai.local
127.0.0.1 adminapps.isosmart.local adminapps.smart3ai.local sso.smart3ai.local
```

Suggested command:

```bash
sudo sh -c 'cat >> /etc/hosts <<EOF
127.0.0.1 medsupplier.isosmart.local medsupplier.smart3ai.local
127.0.0.1 isosmart.local isosmart.smart3ai.local smart3ai.local
127.0.0.1 adminapps.isosmart.local adminapps.smart3ai.local sso.smart3ai.local
EOF'
```

Then verify:

```bash
getent hosts medsupplier.isosmart.local isosmart.local adminapps.isosmart.local
curl -I http://medsupplier.isosmart.local/
curl -I http://isosmart.local/
curl -I http://adminapps.isosmart.local/
```

## Browser Access Rule Until SSL Exists

Use HTTP locally:

```text
http://medsupplier.isosmart.local/
http://isosmart.local/
http://adminapps.isosmart.local/
```

Do not use HTTPS locally until the DNS/SSL go-live runbook has been executed and Nginx is listening on port 443.

## Remaining Blocker

Local browser access to ISO Smart and AdminApps remains blocked until `/etc/hosts` is updated with sudo privileges. This is an operating-system permission blocker, not an application runtime blocker.
