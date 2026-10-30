# Architecture Baseline Report - Ecosistema ISO Smart

Fecha: 2026-06-27

## 1. MedSupplier

- Backend detectado: Django/DRF en `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend`.
- Frontend detectado: React/Vite en `/home/felipe/proyectos/ISO_Smart_MedSupplier/frontend`.
- App Django real: `backend/medsupplier`, en su propio repo. No vive dentro de `/home/felipe/proyectos/isosmart`.
- Apps instaladas: incluye `medsupplier`, `authentication`, `core`, `integration`, `leadership`, `resources`, `planning`, `operations`, `performance`, `improvement` y modulos ISO heredados `ai_modules.sca/sie/asb/spm`.
- Tests existentes: `backend/medsupplier/tests.py`, 26 tests pasados con `backend/.venv312` propio.
- E2E existente: `frontend/tests/e2e/medsupplier-demo-runtime.spec.js`, 5 tests pasados.
- Entorno virtual: se creo y valido `backend/.venv312`.
- Dependencias: existia `requirements.txt` en raiz; se agregaron `backend/requirements.txt` y `backend/requirements-dev.txt`.
- Migraciones: `medsupplier/0001_initial.py` y `0002_evidencepackage_evidencepackageentry_and_more.py`.
- Documentacion: docs compliance, security, validation e internal ya existentes; se agregan reportes internos de ecosistema.
- Estado git inicial: existia documento untracked `docs/internal/MEDSUPPLIER_BASELINE_MIGRATION_FIX_2026-06-27.md`.
- Riesgos: dependencia historica de patrones ISO dentro del repo MedSupplier, nombres/textos ISO-centric y fallback AdminApps local solo apto para dev/demo.

## 2. Iso Smart

- Que se usara como benchmark: hardening Django, settings, logging, middleware, UI/UX, estructura React/Vite, patrones de permisos y documentacion.
- Que NO se copiara: modulos funcionales ISO, apps SCA/SIE/ASB/SPM como producto MedSupplier, datos, migraciones o logica comercial ISO.
- Patrones tecnicos utiles: `settings_test`, SSO/JWT, middleware de organizacion, audit logging, throttling, estructura modular.
- Patrones visuales utiles: layout operativo, sidebar, dashboards densos, componentes de settings y tablas.
- Hardening util: `DEBUG=False` por defecto, cookies secure por env, `X_FRAME_OPTIONS`, `SECURE_CONTENT_TYPE_NOSNIFF`, referrer policy y throttling DRF.
- Accesibilidad util: patrones de navegacion y componentes reutilizables conceptualmente.
- Dependencias que NO deben mezclarse: dependencias especificas de IA/ISO o modulos QMS que no sean requeridos por MedSupplier.
- Estado git: repo separado, no modificado.
- Riesgos: usar su venv como workaround puede ocultar que MedSupplier no tenia entorno propio; no debe ser contrato release.

## 3. AdminApps

- Backend detectado: Django/DRF en `/home/felipe/proyectos/adminapps/backend`.
- Frontend detectado: React/Vite en `/home/felipe/proyectos/adminapps/frontend`.
- Modelos de organizacion: `apps.organizations.Organization`, con status, contacto, plan/suscripcion y metadata.
- Modelos de usuario: `apps.users.User` y `UserOrganization`, con roles globales/organizacionales.
- Modelos de producto/sistema: parcialmente. `apps.billing.ProductCatalog` es producto-neutral, pero `apps.products` sigue ISO-centric (`ISOStandard`, `OrganizationModule`).
- Modelos de plan: `apps.subscriptions.Plan`, con `modules_included`.
- Modelos de suscripcion: `apps.subscriptions.Subscription`.
- Modelos de billing: `apps.billing.FiscalProfile`, `ProductCatalog`, `ProductPrice`, `ElectronicInvoice`, `InvoiceLine`, pagos y reportes.
- Modelo de entitlements: existe como `OrganizationModule`, pero sigue semantica ISO/module; no es aun `OrganizationProduct` producto-neutral.
- Integracion posible con MedSupplier: endpoint `/api/integration/organizations/{id}/modules/` mapea `medsupplier` a `MEDSUPPLIER`; falta endpoint producto-neutral explicito con billing/subscription status.
- Estado git: no se modifico durante la fase read-only; luego se documentaron brechas desde MedSupplier.
- Riesgos: `makemigrations --check` falla, tests 2FA fallan, frontend no tiene `lint`, `STATICFILES_DIRS` apunta a directorio inexistente, y el catalogo products sigue ISO-centrico.

## 4. Decision tecnica

- Arquitectura recomendada: tres productos/repos separados; AdminApps como control plane producto-neutral; MedSupplier consume AdminApps por API interna con fallback local solo dev/demo y permisos locales estrictos.
- Que se debe corregir primero: baseline AdminApps (`makemigrations`, tests 2FA, producto-neutral products/entitlements).
- Que se debe construir: `Product/System Catalog` y `OrganizationProduct` en AdminApps o migracion compatible desde `OrganizationModule`.
- Que se debe documentar: contrato de validacion, herencia ISO, benchmark Iso Smart, hardening y release readiness.
- Que se debe probar: MedSupplier backend/frontend/E2E, AdminApps products/organizations/users/entitlements/billing, denegacion de producto no habilitado.
- Que NO se debe hacer: mover MedSupplier dentro de Iso Smart, crear app falsa en Iso Smart, usar `migrate --fake`, borrar migraciones o declarar cumplimiento regulado completo.
