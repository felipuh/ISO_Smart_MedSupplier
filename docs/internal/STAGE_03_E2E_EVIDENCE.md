# Stage 03 E2E Evidence

Fecha: 2026-06-29

## Objetivo

Ejecutar el E2E real de MedSupplier con backend y frontend propios, validar flujos demo/MVP y documentar cobertura, evidencia y brechas.

## Comando ejecutado

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier/frontend
npm run test:e2e:medsupplier
```

## Resultado

Estado: PASS

Resumen Playwright:

```text
Running 5 tests using 1 worker
5 passed (1.0m)
```

El seed demo fue ejecutado por el spec usando el Python propio de MedSupplier:

```text
MedSupplier demo seeded for organization MedSupplier Demo Workspace (medsupplier-demo-e2e).
Accounts: MS-DEMO-001, MS-DEMO-PRIVATE.
User: medsupplier.e2e@smart3ai.local
```

Archivo de resultado Playwright:

`frontend/test-results/.last-run.json`

Contenido relevante:

```json
{
  "status": "passed",
  "failedTests": []
}
```

No se generaron screenshots ni videos porque no hubo fallos.

## Entorno usado

| Area | Ruta/valor | Estado |
| --- | --- | --- |
| Repo | `/home/felipe/proyectos/ISO_Smart_MedSupplier` | PASS |
| Backend server | `../backend` via Playwright webServer | PASS |
| Python backend | `/home/felipe/proyectos/ISO_Smart_MedSupplier/backend/.venv312/bin/python` | PASS |
| Frontend server | Vite en `127.0.0.1:3001` | PASS |
| API proxy | `http://127.0.0.1:18002` | PASS |
| Demo org | `medsupplier-demo-e2e` | PASS |

Observacion: durante el arranque, `/health` respondio `401 Unauthorized`, pero Playwright continuo y el E2E completo paso. Esto queda como brecha de readiness/healthcheck para hardening, no como falla funcional del E2E MedSupplier.

## Flujos cubiertos

| Flujo | Estado | Evidencia |
| --- | --- | --- |
| Login demo | PASS | Todos los tests inician sesion y obtienen access token. |
| Navegacion a MedSupplier | PASS | Se navega a accounts, documents, quotes y cockpit. |
| Seed demo reproducible | PASS | `seed_medsupplier_demo` corre en `beforeAll`. |
| Creacion de account por supplier autorizado | PASS | Supplier finance crea cuenta `E2E-*` y la ve listada. |
| Document Room visible | PASS | Se verifica `MS-DOC-COC-001`. |
| Acciones bloqueadas en UI | PASS | Botones de aprobacion/rechazo aparecen disabled donde corresponde. |
| Supplier autorizado ve cockpit privado | PASS | Supplier finance ve `Cockpit privado Supplier` y `Margen promedio`. |
| Customer no ve cockpit privado | PASS | Customer roles reciben 403 en `/medsupplier/cockpit/private/`. |
| Customer no ve cuenta privada | PASS | Customers ven `MS-DEMO-001` y no ven `MS-DEMO-PRIVATE`. |
| Customer no ve datos financieros privados | PASS | Quote payload no expone campos privados. |
| Supplier Quality/Logistics no ven finanzas privadas | PASS | No reciben `supplier_cost` ni `margin`. |
| Viewer read-only | PASS | Supplier viewer no ve boton `Nuevo` y mutacion devuelve 403. |
| Customer Auditor read-only | PASS | Auditor puede leer evidence package y mutacion devuelve 403. |
| Acceso no autorizado bloqueado | PASS | Mutaciones sin permiso devuelven 403. |

## Roles cubiertos

| Rol E2E | Usuario | Cobertura |
| --- | --- | --- |
| Supplier Finance | `medsupplier.e2e@smart3ai.local` | Login, cockpit privado, datos financieros, creacion account. |
| Supplier Quality | `medsupplier.supplier.quality@smart3ai.local` | Denegacion cockpit privado, ocultamiento financiero. |
| Supplier Logistics | `medsupplier.supplier.logistics@smart3ai.local` | Denegacion cockpit privado, ocultamiento financiero. |
| Supplier Viewer | `medsupplier.supplier.viewer@smart3ai.local` | Read-only UI y backend 403 en mutacion. |
| Customer Buyer | `medsupplier.customer.buyer@smart3ai.local` | Scope customer, 403 cockpit, sin privados, mutacion 403. |
| Customer Quality | `medsupplier.customer.quality@smart3ai.local` | Scope customer, 403 cockpit, sin privados, mutacion 403. |
| Customer Auditor | `medsupplier.customer.auditor@smart3ai.local` | Lectura evidence package, 403 cockpit, mutacion 403. |
| Customer Viewer | `medsupplier.customer.viewer@smart3ai.local` | Scope customer, 403 cockpit, sin privados, mutacion 403. |

## Campos privados verificados

El E2E valida que clientes no reciban:

- `private_margin_notes`
- `supplier_cost`
- `margin`
- `commission`
- `advance`
- `internal_notes`
- `pricing_internal`

Tambien valida que Supplier Quality y Supplier Logistics no reciban:

- `supplier_cost`
- `margin`

## Gate de aceptacion

| Criterio | Estado | Evidencia |
| --- | --- | --- |
| E2E ejecutado. | PASS | `npm run test:e2e:medsupplier`. |
| E2E pasa. | PASS | 5 tests passed. |
| No usa venv ISO Smart como default. | PASS | Spec usa `ISO_Smart_MedSupplier/backend/.venv312/bin/python`; Playwright webServer usa `../backend/.venv312`. |
| Evidencia guardada. | PASS | Este reporte y `frontend/test-results/.last-run.json`. |
| Brechas documentadas. | PASS | Ver seccion Brechas. |

## Brechas

### P0

Ninguna.

### P1

Ninguna para el gate de ETAPA 3.

### P2

- `/health` respondio `401 Unauthorized` durante el arranque del webServer. Para production-like readiness deberia existir un healthcheck publico o un readiness check autenticado/documentado segun arquitectura. Corresponde a ETAPA 8.
- La cobertura E2E no reemplaza la matriz endpoint/rol completa. Corresponde a ETAPA 6.

### P3

- No hay screenshots/videos porque la corrida paso sin fallos. Si se requiere evidencia visual para auditoria comercial, puede configurarse captura `on` en una corrida dedicada.

## Riesgos

- E2E usa seed demo local; no prueba todavia integracion real AdminApps sin fallback. Eso corresponde a ETAPA 5.
- E2E cubre roles principales, pero no todos los endpoints minimos de la matriz enterprise. Eso corresponde a ETAPA 6.
- El healthcheck 401 puede confundir readiness automatizado en CI/CD si no se ajusta antes de pipeline formal.

## Decision

Estado: aprobado con observaciones.

Decision: ETAPA 3 completada.

Se puede avanzar a ETAPA 4: si.
