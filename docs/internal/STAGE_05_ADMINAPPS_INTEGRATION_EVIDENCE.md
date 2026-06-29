# Stage 05 AdminApps Integration Evidence

Fecha: 2026-06-29

## Objetivo

Hacer que MedSupplier valide acceso contra AdminApps mediante contrato producto-neutral, y que el fallback local solo opere en demo/test de forma explicita, segura y documentada.

## Cambios implementados

| Area | Cambio | Estado |
| --- | --- | --- |
| Cliente AdminApps | Se agrego `validate_product_access(org_id, product_code)` usando `/products/{product_code}/validate/`. | PASS |
| Contrato MedSupplier | `integration_status` usa validacion producto-neutral para `MEDSUPPLIER`. | PASS |
| Smoke command | `check_medsupplier_adminapps` usa `validate_product_access`. | PASS |
| Fallback | Fallback local requiere `ADMIN_APPS_ALLOW_LOCAL_FALLBACK=True` y `IS_PRODUCTION=False`. | PASS |
| Produccion | Si AdminApps falla en produccion, el acceso falla cerrado. | PASS |
| Denegaciones negocio | `allowed=False` desde AdminApps no se bypass-ea, incluyendo `billing_blocked`. | PASS |
| Settings test | `settings_test` fija `ENVIRONMENT=test`, `IS_PRODUCTION=False` y fallback local explicito. | PASS |

## Contrato runtime

MedSupplier valida:

```http
GET /api/integration/organizations/{organization_id}/products/MEDSUPPLIER/validate/
X-API-Key: <internal-api-key>
```

MedSupplier permite acceso solo si AdminApps responde:

```json
{
  "allowed": true,
  "reason": "ok",
  "product": {
    "code": "MEDSUPPLIER",
    "access_allowed": true
  }
}
```

## Reglas de fallback

Fallback local solo puede activar acceso cuando:

1. `ADMIN_APPS_ALLOW_LOCAL_FALLBACK=True`.
2. `IS_PRODUCTION=False`.
3. El producto solicitado es `MEDSUPPLIER`.
4. La organizacion local existe y esta activa.
5. La organizacion tiene al menos un `MedSupplierUserScope` activo.

Fallback local no se usa cuando AdminApps responde una denegacion de negocio, por ejemplo:

- `product_not_enabled`
- `billing_not_configured`
- `billing_blocked`
- `entitlement_disabled`
- `entitlement_inactive`
- `entitlement_expired`

## Comandos ejecutados

| Repo | Comando | Resultado | Observacion |
| --- | --- | --- | --- |
| MedSupplier | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check` | PASS | 0 issues |
| MedSupplier | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py makemigrations --check --dry-run` | PASS | No changes detected |
| MedSupplier | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py test medsupplier` | PASS | 29 tests OK |
| MedSupplier | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e` | PASS | Fallback local explicito demo/test; 10 scopes activos |
| AdminApps | `DJANGO_SETTINGS_MODULE=config.settings_test ./.venv312/bin/python manage.py test apps.products` | PASS | 8 tests OK |

## Smoke output relevante

```text
organization=3 slug=medsupplier-demo-e2e
adminapps_available=True
product_access_source=local_database
medsupplier_entitlement_enabled=True
medsupplier_access_reason=ok
active_medsupplier_scopes=10
AdminApps fallback local explicito activo: solo demo/test, no produccion; el acceso sigue limitado por MedSupplierUserScope y no sustituye billing real.
MedSupplier AdminApps smoke passed.
```

Observacion: el AdminApps local en `http://127.0.0.1:8000` respondio 404 para:

```text
/api/integration/organizations/3/products/MEDSUPPLIER/validate/
```

Por eso el smoke paso usando fallback local explicito de `settings_test`. No se declara integracion real staging/produccion en esta etapa.

## Pruebas agregadas

| Prueba | Valida |
| --- | --- |
| `test_product_access_uses_explicit_local_fallback_only_with_scope` | Fallback demo/test requiere scope local activo. |
| `test_product_access_does_not_bypass_adminapps_business_denial` | `billing_blocked` desde AdminApps no se bypass-ea. |
| `test_product_access_fails_closed_in_production_when_adminapps_unavailable` | Produccion falla cerrado aunque el flag este activo. |
| `test_integration_status_declares_adminapps_as_authority` | Status MedSupplier reporta autoridad AdminApps y producto `MEDSUPPLIER`. |

## Gate de aceptacion

| Criterio | Estado | Evidencia |
| --- | --- | --- |
| Smoke pasa contra AdminApps real o fallback queda marcado demo/dev. | PASS con observacion | Smoke paso con fallback local explicito `settings_test`; endpoint real local respondio 404. |
| Produccion no permite fallback silencioso. | PASS | Tests cubren `IS_PRODUCTION=True` fail-closed. |
| Tests cubren denegacion. | PASS | `billing_blocked` no se bypass-ea. |
| No hay apertura global de permisos. | PASS | Fallback requiere `MedSupplierUserScope` activo. |
| Documentacion actualizada. | PASS | Este reporte y contrato previo AdminApps-MedSupplier. |

## Brechas

### P0

Ninguna.

### P1

- Integracion real contra AdminApps local/staging no queda verde porque el endpoint producto-neutral devolvio 404 en `http://127.0.0.1:8000`. La etapa queda aprobada con fallback demo/test explicito, no como smoke real production-like.

### P2

- El cliente AdminApps conserva metodos legacy con fallback para organizaciones/modulos por compatibilidad con ISO Smart. MedSupplier ya no depende de esos metodos para su entitlement.
- `is_module_enabled()` sigue basado en `/modules/` para consumidores legacy; no debe usarse para MedSupplier.

### P3

- Algunos textos del cliente siguen en espanol orientado a ISO Smart; no bloquean el contrato funcional.

## Riesgos

- Antes de release candidate, AdminApps real debe exponer `/products/MEDSUPPLIER/validate/` en el ambiente usado por MedSupplier.
- El fallback demo/test no prueba billing real; solo evita bloqueo local mientras se integran ambientes.
- CI debe fijar explicitamente `DJANGO_SETTINGS_MODULE=backend.settings_test` para permitir fallback demo/test controlado.

## Decision

Estado: aprobado con observaciones.

Decision: ETAPA 5 completada.

Se puede avanzar a ETAPA 6: si, manteniendo como brecha P1 la falta de smoke real contra AdminApps staging/local compatible.
