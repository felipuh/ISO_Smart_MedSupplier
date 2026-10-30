# AdminApps MedSupplier Contract

Fecha: 2026-06-29

## Objetivo

Documentar como MedSupplier debe consumir AdminApps para validar acceso producto-neutral, entitlement, suscripcion y billing.

Fuente canonica:

`/home/felipe/proyectos/adminapps/docs/PRODUCT_NEUTRAL_ADMINAPPS_CONTRACT.md`

## Producto

MedSupplier se identifica como:

```text
MEDSUPPLIER
```

No debe validarse como modulo ISO legacy.

## Endpoint requerido

```http
GET /api/integration/organizations/{organization_id}/products/MEDSUPPLIER/validate/
X-API-Key: <internal-api-key>
```

MedSupplier debe permitir acceso solo si:

```json
{
  "allowed": true,
  "reason": "ok",
  "product": {
    "code": "MEDSUPPLIER",
    "access_allowed": true,
    "access_denial_reason": "ok",
    "billing_status": "active"
  }
}
```

## Denegaciones obligatorias

MedSupplier debe denegar acceso si AdminApps responde:

| Razon | Accion MedSupplier |
| --- | --- |
| `organization_inactive` | Denegar acceso. |
| `product_not_enabled` | Denegar acceso. |
| `entitlement_disabled` | Denegar acceso. |
| `entitlement_inactive` | Denegar acceso. |
| `entitlement_expired` | Denegar acceso. |
| `product_unavailable` | Denegar acceso. |
| `billing_not_configured` | Denegar acceso salvo modo demo/dev explicito y auditado. |
| `billing_blocked` | Denegar acceso. |

## Reglas para fallback

Fallback local solo puede existir en demo/dev:

1. Debe estar detras de flag explicito.
2. Debe quedar auditado/logueado como fallback.
3. No debe operar en produccion.
4. No debe abrir permisos globales.
5. No debe reemplazar la denegacion por billing bloqueado.

La implementacion completa de fallback seguro corresponde a ETAPA 5.

## Evidencia AdminApps

El contrato fue validado con:

```bash
cd /home/felipe/proyectos/adminapps/backend
DJANGO_SETTINGS_MODULE=config.settings_test ./.venv312/bin/python manage.py check
DJANGO_SETTINGS_MODULE=config.settings_test ./.venv312/bin/python manage.py makemigrations --check --dry-run
DJANGO_SETTINGS_MODULE=config.settings_test ./.venv312/bin/python manage.py test apps.products apps.billing apps.users apps.api
```

Resultado:

- `check`: PASS.
- `makemigrations --check --dry-run`: PASS.
- tests AdminApps focalizados: PASS, 123 tests OK.

## Decision

Estado: aprobado con observaciones.

MedSupplier puede avanzar a ETAPA 5 para integrar este contrato sin fallback permisivo.
