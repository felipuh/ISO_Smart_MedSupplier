# Iso Smart Benchmark For MedSupplier - 2026-06-27

Iso Smart se usa como referencia tecnica, visual y de seguridad. No es contenedor de MedSupplier.

## Se toma como referencia

- Stack Django/DRF + React/Vite.
- Settings separados para test.
- Multi-tenant por organizacion.
- SSO/JWT y sincronizacion con AdminApps.
- Throttling DRF.
- Auditoria de cambios y request id.
- Layout operativo con navegacion lateral, dashboards densos y pantallas de trabajo.
- Documentacion de security, validation y compliance-ready language.

## No se copia

- Apps funcionales ISO como si fueran dominio MedSupplier.
- Migraciones o datos de Iso Smart.
- Modulos SCA/SIE/ASB/SPM como obligatorios de producto MedSupplier.
- Claims regulatorios absolutos.
- Dependencia del venv de Iso Smart como contrato de release.

## Se replica conceptualmente

- Hardening por entorno.
- Convenciones de APIs REST.
- Patrones de permisos por rol y organizacion.
- Estructura de QA con backend check, tests, frontend lint/build y E2E.

## Se debe adaptar

- Producto-neutral entitlements desde AdminApps.
- Vocabulario Supplier-Customer.
- RBAC/ABAC propio: supplier/customer/auditor/finance/logistics/quality.
- Audit trail y evidence package especificos del dominio MedSupplier.

## No aplica

- Gestion de normas ISO como catalogo principal.
- Clausulas ISO como unidad de venta de MedSupplier.
- Workflows QMS genericos cuando no pertenecen al workspace Supplier-Customer.

## Riesgos de acoplamiento

- Settings y dependencias heredadas pueden dar falsa impresion de producto integrado.
- Usar venv de Iso Smart oculta faltantes de requirements propios.
- Reutilizar terminos "module" para productos puede limitar venta separada.
