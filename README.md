# ISO Smart MedSupplier

ISO Smart MedSupplier es una torre de control regulada Supplier-Customer para clientes de Medical Devices y empresas transnacionales.

El producto se diseña como un workspace regulado para colaboración, trazabilidad, calidad, órdenes, documentación, CAPA, riesgos y desempeño del suplidor. Esta base es compliance-ready, audit-ready, validation-ready, Part 11-ready y QMS-ready; el cumplimiento formal depende de validación, SOPs, capacitación, controles operativos y uso real de cada organización.

## Modelo comercial y técnico

ISO Smart MedSupplier no es una copia visual/funcional de Iso Smart. Es un producto vertical Supplier-Customer. AdminApps es siempre el cerebro comercial del ecosistema: las organizaciones cliente, usuarios, roles, suscripciones y habilitación del módulo `MEDSUPPLIER` se crean y gobiernan ahí.

- **Standalone comercial**: se vende por separado de Iso Smart y puede operar con su propia base de datos, dominio, backend, frontend y registros regulados, pero identidad, organizaciones y licenciamiento siguen viniendo de AdminApps.
- **Integrado**: si el cliente compra Iso Smart + MedSupplier, comparte autoridad de identidad/AdminApps y además puede conectar evidencia QMS, flujos de calidad y contexto organizacional con Iso Smart.

La línea base de Iso Smart se usa para colores, hardening, seguridad, arquitectura, stack y patrones de calidad, no para convertir MedSupplier en una réplica de módulos ISO.

## Base técnica

- Línea base: `/home/felipe/proyectos/isosmart`
- Integración ecosistema: `/home/felipe/proyectos/adminapps`
- Backend: Django, Django REST Framework, PostgreSQL, SimpleJWT/SSO Smart3AI
- Frontend: React, Vite, Tailwind, Axios
- Multi-tenant: `core.Organization` y `authentication.UserProfile`
- Gobierno central: AdminApps como fuente de verdad para clientes, usuarios, roles y entitlement `MEDSUPPLIER`
- Permisos iniciales: `org_admin`, `iso_manager`, `user`, `auditor`, `viewer`
- Configuración standalone: `backend/.env.medsupplier.example`

## MVP incluido

- App backend `medsupplier`
- APIs bajo `/api/medsupplier/`
- Cliente 360 básico
- Reuniones, minutas y acciones
- Requisitos
- Document Room con versiones
- RFQ/cotización
- PO, lotes, shipments e inspección
- NCR/queja/deviation como quality events
- CAPA básica
- Scorecards/QBR básico
- Audit events del módulo
- Dashboard inicial en `/medsupplier`
- Workspace propio: Cliente 360, reuniones, acciones, requisitos, Document Room, RFQ, cotizaciones, órdenes, shipments, calidad, CAPA, scorecards, audit trail e integración.
- Estado de integración AdminApps en `/api/medsupplier/integration/status/`

## Visibilidad

- `shared`: workspace compartido Supplier-Customer
- `private`: workspace privado interno

La información comercial privada debe permanecer marcada como `private` y no exponerse a usuarios cliente.

## Validación local

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier/backend
DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py test medsupplier
```
