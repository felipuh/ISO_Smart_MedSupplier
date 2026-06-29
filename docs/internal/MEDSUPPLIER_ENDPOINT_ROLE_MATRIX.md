# MedSupplier Endpoint Role Matrix

Fecha: 2026-06-29

## Objetivo

Cerrar la brecha de seguridad funcional de MedSupplier con una matriz endpoint/rol ejecutable para RBAC/ABAC, privacidad comercial, mutaciones, cross-tenant y cross-account.

## Comandos ejecutados

| Repo | Comando | Resultado | Observacion |
| --- | --- | --- | --- |
| MedSupplier | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check` | PASS | 0 issues |
| MedSupplier | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py makemigrations --check --dry-run` | PASS | No changes detected |
| MedSupplier | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py test medsupplier.tests.MedSupplierEndpointRoleMatrixTests` | PASS | 11 matrix tests OK |
| MedSupplier | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py test medsupplier` | PASS | 40 tests OK |

## Roles cubiertos

| Grupo | Roles |
| --- | --- |
| Supplier | `supplier_admin`, `supplier_sales`, `supplier_finance`, `supplier_quality`, `supplier_logistics`, `supplier_viewer` |
| Customer | `customer_admin`, `customer_buyer`, `customer_quality`, `customer_logistics`, `customer_auditor`, `customer_viewer` |

## Endpoints minimos cubiertos

| Requisito | Endpoint real | Estado |
| --- | --- | --- |
| accounts | `/api/medsupplier/accounts/` | PASS |
| summary | `/api/medsupplier/dashboard/summary/` | PASS |
| me/permissions | `/api/medsupplier/me/permissions/` | PASS |
| quotes | `/api/medsupplier/quotes/` | PASS |
| orders | `/api/medsupplier/purchase-orders/` | PASS |
| shipments | `/api/medsupplier/shipments/` | PASS |
| documents | `/api/medsupplier/documents/` | PASS |
| capas | `/api/medsupplier/capas/` | PASS |
| fmea | `/api/medsupplier/fmeas/` | PASS |
| evidence-packages | `/api/medsupplier/evidence-packages/` | PASS |
| cockpit/private | `/api/medsupplier/cockpit/private/` | PASS |
| audit-trail | `/api/medsupplier/audit-events/` and `/api/medsupplier/audit-events/export/` | PASS |
| integration/status | `/api/medsupplier/integration/status/` | PASS |

## Validaciones ejecutables

| Validacion | Estado | Test |
| --- | --- | --- |
| Supplier Admin puede leer endpoint matrix minimo. | PASS | `test_supplier_admin_can_read_minimum_endpoint_matrix` |
| Customer no ve cockpit privado. | PASS | `test_private_cockpit_access_is_limited_to_authorized_supplier_roles` |
| Customer no ve cuentas privadas. | PASS | `test_customer_roles_are_scoped_and_do_not_see_private_or_unscoped_accounts` |
| Customer no ve cuentas fuera de account_scope. | PASS | `test_customer_roles_are_scoped_and_do_not_see_private_or_unscoped_accounts` |
| Customer no ve `supplier_cost`. | PASS | `test_customer_roles_do_not_receive_private_financial_quote_fields` |
| Customer no ve `margin`. | PASS | `test_customer_roles_do_not_receive_private_financial_quote_fields` |
| Customer no ve `commission`. | PASS | `test_customer_roles_do_not_receive_private_financial_quote_fields` |
| Customer no ve `advance`. | PASS | `test_customer_roles_do_not_receive_private_financial_quote_fields` |
| Customer no ve `internal_notes`. | PASS | `test_customer_roles_do_not_receive_private_financial_quote_fields` |
| Customer no ve `private_margin_notes`. | PASS | `test_customer_roles_do_not_receive_private_financial_quote_fields` |
| Supplier Logistics no ve campos financieros privados. | PASS | `test_supplier_quality_and_logistics_do_not_receive_private_financial_quote_fields` |
| Supplier Quality no ve campos financieros privados. | PASS | `test_supplier_quality_and_logistics_do_not_receive_private_financial_quote_fields` |
| Supplier Finance si ve campos financieros privados. | PASS | `test_supplier_finance_can_receive_private_financial_quote_fields` |
| Supplier Viewer no escribe. | PASS | `test_read_only_and_customer_roles_cannot_mutate_accounts` |
| Customer Auditor no escribe. | PASS | `test_customer_audit_trail_is_read_only_and_redacted` |
| Customer roles no escriben. | PASS | `test_read_only_and_customer_roles_cannot_mutate_accounts` |
| Mutaciones sin permiso devuelven 403. | PASS | `test_read_only_and_customer_roles_cannot_mutate_accounts` |
| Cross-tenant bloqueado. | PASS | `test_cross_tenant_access_is_blocked` |
| Cross-account bloqueado/oculto. | PASS | `test_customer_detail_outside_account_scope_is_hidden` |
| Objetos fuera de scope devuelven 404 seguro. | PASS | `test_customer_detail_outside_account_scope_is_hidden` |
| Audit trail customer se redacted. | PASS | `test_customer_audit_trail_is_read_only_and_redacted` |
| Mutacion autorizada genera audit event. | PASS | `test_supplier_admin_can_mutate_and_audit_event_is_created` |

## Campos privados protegidos

Los tests verifican que Customer, Supplier Quality y Supplier Logistics no reciban:

- `private_margin_notes`
- `supplier_cost`
- `margin`
- `commission`
- `advance`
- `internal_notes`
- `pricing_internal`
- `forecast_probability`

Cambio implementado:

`BaseMedSupplierSerializer.get_fields()` ahora remueve todo `PRIVATE_COMMERCIAL_FIELDS` para cualquier rol que no tenga `can_view_private_financials`.

## Politica aplicada

| Politica | Implementacion |
| --- | --- |
| Permisos backend, no solo frontend | `MedSupplierCanEdit`, `resolve_medsupplier_context`, `assert_can_mutate`, `filter_queryset_for_context`. |
| Supplier private cockpit limitado | Solo `supplier_admin`, `supplier_finance`, `supplier_sales`. |
| Privacidad comercial | Serializer elimina campos privados por contexto. |
| Customer account scope | Customer solo accede a `account_ids` de `MedSupplierUserScope`. |
| Cross-tenant | Sin scope de organizacion, `resolve_medsupplier_context` deniega. |
| Objetos fuera de scope | Queryset filtrado devuelve 404 seguro. |
| Audit trail customer | Oculta `old_values`, `new_values`, `ip_address`, `user_agent`. |

## Gate de aceptacion

| Criterio | Estado | Evidencia |
| --- | --- | --- |
| Matriz ejecutada. | PASS | `MedSupplierEndpointRoleMatrixTests`, 11 tests OK. |
| Tests pasan. | PASS | Suite MedSupplier completa: 40 tests OK. |
| No hay exposicion privada. | PASS | Campos privados removidos para customers y supplier non-finance. |
| No hay cross-tenant. | PASS | Cross-tenant devuelve 403. |
| No hay permisos solo frontend. | PASS | Mutaciones bloqueadas por backend con 403. |

## Brechas

### P0

Ninguna.

### P1

Ninguna para el gate de ETAPA 6.

### P2

- El endpoint requerido como `orders` existe en la API actual como `purchase-orders`. Se documenta esta equivalencia; no se crea alias en esta etapa para evitar cambio de superficie API sin decision de producto.
- La matriz cubre endpoints minimos y seguridad funcional, pero no sustituye pruebas profundas de cada modulo enterprise. Eso corresponde a ETAPA 7.

### P3

- Los tests de matriz son backend/API. La cobertura visual E2E de cada endpoint puede ampliarse posteriormente si se requiere evidencia comercial visual.

## Decision

Estado: aprobado con observaciones.

Decision: ETAPA 6 completada.

Se puede avanzar a ETAPA 7: si.
