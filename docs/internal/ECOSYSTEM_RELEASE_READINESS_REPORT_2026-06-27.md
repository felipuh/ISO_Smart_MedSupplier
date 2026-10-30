# Ecosystem Release Readiness Report - ISO Smart / MedSupplier / AdminApps

## 1. Resumen ejecutivo

- Estado general: MedSupplier funcional para demo controlada; AdminApps bloquea RC serio del ecosistema.
- Apto para demo controlada: si, para MedSupplier standalone/demo local.
- Apto para MVP enterprise controlado: parcialmente, requiere limpiar AdminApps.
- Apto para release candidate: no.
- Apto para produccion regulada completa: no.
- Decision: no aprobado para RC ecosistema; aprobado solo para continuar sprint RC.

## 2. Arquitectura final

- ISO Smart: producto separado y benchmark.
- MedSupplier: producto independiente con backend/frontend propios.
- AdminApps: control plane comercial/administrativo; aun debe volverse producto-neutral en `apps.products`.
- Relacion entre productos: venta conjunta o separada.
- Venta conjunta/separada: soportada conceptualmente; AdminApps debe completar `OrganizationProduct`/entitlement neutral.

## 3. Contrato AdminApps

- Products: parcial; `ProductCatalog` billing-neutral existe, `ISOStandard/OrganizationModule` sigue ISO-centric.
- Organizations: existe.
- Users: existe.
- Entitlements: parcial via `OrganizationModule`/plan `modules_included`.
- Billing: existe y tiene catalogo producto-neutral.
- Subscriptions: existe.
- `MEDSUPPLIER` enabled: soportado por mapa de integracion cuando `modules_included` contiene `medsupplier`.
- `ISO_SMART` enabled: no queda formalizado como producto neutral equivalente.
- Estado: requiere correccion P0/P1 antes de RC.

## 4. MedSupplier

- Backend: Django/DRF propio, tests pasan con `backend/.venv312` propio.
- Frontend: React/Vite, lint/build/E2E pasan.
- Tests: 26 backend OK.
- E2E: 5 Playwright OK.
- RBAC/ABAC: supplier/customer/read-only/cockpit privado validado por tests.
- Document Room: implementado.
- CAPA: implementado.
- FMEA: modelo/API implementado.
- EvidencePackage: implementado.
- Audit Trail: implementado.
- Hardening: parcial.
- Validation docs: existentes y ampliadas.
- Estado: demo controlada aprobable; RC depende de venv propio validado y AdminApps.

## 5. Iso Smart benchmark

- Que se tomo: patrones de stack, seguridad, UX, permisos, docs.
- Que no se copio: MedSupplier no se movio a Iso Smart.
- Riesgos: dependencia temporal del venv de Iso Smart.
- Estado: solo referencia.

## 6. Comandos ejecutados

| Producto | Area | Comando | Resultado | Observacion |
| -------- | ---- | ------- | --------- | ----------- |
| MedSupplier | Backend global | `DJANGO_SETTINGS_MODULE=backend.settings_test python manage.py check` | Falla | Python global sin Django. |
| MedSupplier | Backend check | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check` | Pasa | Venv propio. |
| MedSupplier | Migraciones | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py makemigrations --check --dry-run` | Pasa | No changes detected. |
| MedSupplier | Migrate plan | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py migrate --plan` | Pasa | No planned migration operations. |
| MedSupplier | Tests | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py test medsupplier` | Pasa | 26 tests OK. |
| MedSupplier | Smoke | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py seed_medsupplier_demo --organization-slug medsupplier-demo-e2e && DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e` | Pasa | Fallback local controlado; 10 scopes activos. |
| MedSupplier | Frontend lint | `npm run lint` | Pasa | ESLint OK. |
| MedSupplier | Frontend build | `npm run build` | Pasa | Vite OK. |
| MedSupplier | E2E | `npm run test:e2e:medsupplier` | Pasa | 5 tests OK. |
| AdminApps | Check | `DJANGO_SETTINGS_MODULE=config.settings_test ./.venv312/bin/python manage.py check` | Pasa warning | Falta `backend/static`. |
| AdminApps | Migrations check | `DJANGO_SETTINGS_MODULE=config.settings_test ./.venv312/bin/python manage.py makemigrations --check --dry-run` | Falla | Migracion subscriptions pendiente. |
| AdminApps | Tests | `./.venv312/bin/python manage.py test apps.products apps.billing apps.users apps.api` | Falla | 1 failure, 7 errors en 2FA. |
| AdminApps | Frontend build | `npm run build` | Pasa | Vite OK. |
| AdminApps | Frontend lint | `npm run lint` | Falla | Script no definido. |

## 7. Brechas

### P0

- AdminApps no tiene baseline limpio: migracion pendiente y tests 2FA fallando.
- AdminApps products/entitlements no es plenamente producto-neutral.

### P1

- Mantener el contrato MedSupplier en `.venv312` propio y evitar volver al venv de Iso Smart.
- Convertir el fallback local del smoke en modo dev/demo explicitamente deshabilitado para production-like.

### P2

- Revisar y separar dependencias ISO heredadas en MedSupplier.
- Agregar lint AdminApps frontend.
- Crear endpoint producto-neutral de validacion de acceso/billing.

### P3

- Limpiar textos ISO-centric no funcionales.
- Formalizar health/readiness probes.

## 8. Riesgos

- Tecnicos: doble modelo product catalog vs ISO modules en AdminApps.
- Seguridad: fallback local debe quedar dev/demo solamente.
- Regulatorios: no hay validation package formal aprobado.
- Comerciales: venta separada depende de entitlement producto-neutral claro.
- Operativos: AdminApps aun requiere limpieza de baseline antes de RC.

## 9. Decision final

Demo controlada aprobada para MedSupplier. Ecosistema no aprobado para release candidate.

## 10. Proximo sprint recomendado

1. Corregir AdminApps migrations/tests 2FA.
2. Implementar catalogo producto-neutral y `OrganizationProduct`.
3. Validar MedSupplier con `.venv312` propio.
4. Convertir smoke AdminApps en contrato reproducible con seed/precondicion.
