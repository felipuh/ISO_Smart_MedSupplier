# 2026-06-25 - MVP Bootstrap

## Cambios

- Se creó ISO Smart MedSupplier desde la línea base de Iso Smart.
- Se agregó la app Django `medsupplier`.
- Se agregaron modelos, serializers, viewsets, URLs y migración inicial.
- Se agregó dashboard inicial React en `/medsupplier`.
- Se agregó documentación base para validación, compliance y seguridad.
- Se agregaron pruebas de autenticación, scope por organización, aislamiento y permisos.

## Validación

- `manage.py check`: sin issues.
- `makemigrations medsupplier --check --dry-run`: sin cambios pendientes.
- `DJANGO_SETTINGS_MODULE=backend.settings_test manage.py test medsupplier`: OK.

## Notas

El sistema queda preparado como compliance-ready/audit-ready/validation-ready, no como sistema formalmente validado.
