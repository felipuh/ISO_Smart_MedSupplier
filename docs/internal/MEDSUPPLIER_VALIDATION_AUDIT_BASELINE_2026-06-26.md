# MedSupplier Validation Audit Baseline - 2026-06-26

Documento vivo para comparar el avance de ISO Smart MedSupplier hasta llegar a aceptacion 100%.

## 1. Proposito

Esta auditoria deja una linea base medible del estado actual del producto contra el objetivo enterprise regulado:

Cuenta/cliente -> reuniones -> requisitos -> documentos -> RFQ/cotizacion -> validacion/homologacion -> PO -> lote -> shipment -> recepcion/inspeccion -> NCR/queja -> CAPA -> scorecard/QBR.

La auditoria debe actualizarse despues de cada bloque tecnico relevante. Ningun requerimiento puede marcarse como completado sin evidencia real en codigo, configuracion, migraciones, pruebas, endpoints, componentes, permisos, comandos ejecutados o documentacion formal.

## 2. Resultado baseline

- Fecha/hora: 2026-06-26 19:15 CST.
- Resultado global: Parcial.
- Cumplimiento estimado: 62%.
- Estado MVP: funcional basico con CRUD, formularios, endpoints REST, tenant scoping, audit trail inicial y QA parcial.
- Estado comercial: demo/controlado, no listo para venta enterprise regulada completa.
- Estado regulatorio: compliance-ready/audit-ready/validation-ready inicial, no validado formalmente.

## 3. Hallazgos ejecutivos

### Cumplido o razonablemente cubierto

- Producto nombrado oficialmente como ISO Smart MedSupplier.
- Posicionamiento como torre de control regulada Supplier-Customer.
- Stack alineado a Iso Smart: Django/DRF, React/Vite/Tailwind, JWT/SSO, AdminApps.
- Modulo backend `medsupplier` con endpoints REST bajo `/api/medsupplier/`.
- Frontend con workspace propio bajo `/medsupplier`.
- Captura/edicion/eliminacion basica desde UI para modulos principales.
- Flujo MVP cubierto parcialmente: cuenta, contactos, reuniones, acciones, requisitos, documentos, versiones, RFQ, cotizaciones, PO, lotes, shipments, inspecciones, calidad, CAPA y scorecards.
- Tenant isolation inicial por `organization_id`.
- Audit trail inicial con usuario, IP, user-agent, record type, record id, old/new values.
- AdminApps reconocido como autoridad de organizaciones, usuarios, roles, licencias y entitlement `MEDSUPPLIER`.
- Documentacion base en `docs/compliance`, `docs/security`, `docs/validation` y `docs/release-notes`.

### Bloqueos criticos

1. RBAC/ABAC de negocio incompleto.
   - Evidencia: `backend/medsupplier/views.py` usa roles genericos `org_admin`, `iso_manager`, `user`, `auditor`, `viewer`.
   - Riesgo: no distingue Supplier Admin, Asesor Comercial, Supplier Quality, Supplier Ops, Supplier Finance, Cliente Compras, Cliente Calidad, Cliente Recepcion/Logistica ni Auditor Read Only.

2. Exposicion potencial de informacion comercial privada.
   - Evidencia: serializers MedSupplier usan `fields = '__all__'`.
   - Riesgo: `private_margin_notes` puede exponerse si una cotizacion queda como `shared` o si falta un serializer por rol.

3. Separacion shared/private insuficiente para producto regulado.
   - Evidencia: solo existen `shared` y `private`.
   - Riesgo: faltan niveles `supplier_private`, `customer_private`, `internal_commercial_private`, `restricted_quality`, `restricted_finance`, `audit_read_only`, y clases de confidencialidad controladas.

4. Migraciones no limpias.
   - Evidencia: `makemigrations --check --dry-run` detecto migraciones pendientes en `authentication` y `core`.
   - Riesgo: no se puede aceptar release limpio aunque MedSupplier no sea el origen directo.

## 4. Matriz de cumplimiento baseline

| ID | Bloque | Estado | Evidencia | Riesgo | Accion para 100% |
| -- | ------ | ------ | --------- | ------ | ---------------- |
| MS-001 | Naming y posicionamiento | Cumplido | `README.md`, dashboard y API declaran ISO Smart MedSupplier | Bajo | Mantener lenguaje compliance-ready |
| MS-002 | No ERP/SCM generico | Cumplido | README lo define como torre Supplier-Customer | Bajo | Mantener foco vertical |
| MS-003 | Integracion Iso Smart | Parcial | Stack y patrones heredados | Medio | Crear ADR de reutilizacion tecnica |
| MS-004 | Integracion AdminApps | Parcial | Endpoint de status y AdminApps reconoce `MEDSUPPLIER` | Medio | Ejecutar smoke real de entitlement |
| MS-005 | Cliente 360 | Parcial | Modelo, API y UI para cuentas | Medio | Agregar account scope y customer ownership |
| MS-006 | Contactos/stakeholders | Parcial | `SupplierContact` y UI | Medio | Diferenciar roles cliente/proveedor |
| MS-007 | Reuniones/minutas | Parcial | `SupplierMeeting` con agenda/minutes/decisions | Medio | Agregar asistentes normalizados y audit de decisiones |
| MS-008 | Action items | Parcial | `SupplierAction` con owner/due/status | Medio | Agregar ownership real y SLA |
| MS-009 | Requisitos | Parcial | `SupplierRequirement` y relacion RFQ | Medio | Versionado y trazabilidad requirement->document/order |
| MS-010 | Document Room | Parcial | `SupplierDocument`, `SupplierDocumentVersion`, workflow approve | Alto | Aprobaciones formales, firmas, control de obsolescencia |
| MS-011 | Versionado documental | Parcial | Versiones con revision/checksum/aprobacion textual | Alto | Version major/minor, hash obligatorio, approval records |
| MS-012 | RFQ | Parcial | `SupplierRFQ` y workflow send | Medio | Intake completo, revision y historial |
| MS-013 | Quote | Parcial | `SupplierQuote`, workflow approve/reject | Critico | QuoteLine, serializer publico/privado, margen protegido |
| MS-014 | Orders/PO | Parcial | `SupplierPurchaseOrder` | Medio | OrderLine, due date, backlog, discrepancias |
| MS-015 | Lotes | Parcial | `SupplierLot` | Medio | Revision/document link y traceability matrix |
| MS-016 | Shipments | Parcial | `SupplierShipment` | Medio | ShipmentMilestone, ASN, ETA/ETD, POD, incidencias |
| MS-017 | Recepcion/inspeccion | Parcial | `SupplierInspection` | Medio | Plan de inspeccion, defect codes, release/reject controls |
| MS-018 | NCR/queja | Parcial | `SupplierQualityEvent` con tipos ncr/complaint/deviation | Alto | Aging, defect taxonomy, links a lote/revision/orden |
| MS-019 | CAPA | Parcial | `SupplierCAPA`, cierre requiere effectiveness_result | Alto | CAPAAction, verificacion formal y evidencias |
| MS-020 | FMEA | No cumplido | No hay modelo MedSupplier FMEA/FMEAItem | Alto | Implementar o documentar roadmap tecnico con placeholders |
| MS-021 | Scorecard/QBR | Parcial | `SupplierScorecard`, generate-qbr | Medio | KPIs completos, QBR package y aprobaciones |
| MS-022 | Workspace compartido | Parcial | `visibility=shared` y UI | Alto | ABAC por relacion customer/supplier |
| MS-023 | Workspace privado interno | Parcial | `visibility=private` | Alto | Separar comercial/quality/finance/private datasets |
| MS-024 | Cockpit comercial privado | No cumplido | No hay modulo/API dedicado | Critico | Crear cockpit privado Sales/Finance |
| MS-025 | Margen/comisiones/adelantos | No cumplido | Solo `private_margin_notes`; no comisiones/adelantos | Critico | Modelos privados y serializers restringidos |
| MS-026 | RBAC dominio | Bloqueo critico | Roles genericos | Critico | Crear matriz Supplier/Customer/Auditor |
| MS-027 | ABAC dominio | Bloqueo critico | Solo organization + visibility | Critico | Agregar company/account/confidentiality/ownership/state |
| MS-028 | Tenant isolation | Parcial | `OrganizationScopedViewSetMixin` y tests | Alto | Tests cross-tenant por todos los endpoints |
| MS-029 | Serializers seguros | Bloqueo critico | `fields='__all__'` | Critico | Serializers explicitos por rol/visibilidad |
| MS-030 | Audit trail | Parcial | `MedSupplierAuditEvent` | Alto | Hash, correlation_id, reason_code, export immutable |
| MS-031 | E-signature | No cumplido | No hay firma MedSupplier | Alto | Part 11-ready e-signature controls |
| MS-032 | Exportables audit-ready | No cumplido | No hay evidence package MedSupplier | Alto | EvidencePackage y reportes auditables |
| MS-033 | IA governance | Parcial | IA general fuera de MedSupplier | Medio | AIInteractionLog y separacion shared/private |
| MS-034 | Compliance package | Parcial | README placeholders | Alto | URS/FRS/SRS/risk/test evidence reales |
| MS-035 | Frontend forms | Cumplido MVP | `MedSupplierWorkspace.jsx` crea/edita/elimina | Medio | Aplicar permisos UI desde backend |
| MS-036 | Frontend states | Parcial | Loading/error/empty basicos | Bajo | Mejorar states por recurso |
| MS-037 | Pruebas backend | Parcial | `backend/medsupplier/tests.py` | Alto | Completar privacidad comercial y permisos por rol |
| MS-038 | E2E | Parcial | `frontend/tests/e2e/medsupplier-demo-runtime.spec.js` | Medio | Ejecutar en CI y ampliar por rol |
| MS-039 | QA commands | Parcial | `check` y `lint` pasan; migraciones fallan | Alto | Limpiar migraciones y ejecutar build/tests |
| MS-040 | Go-to-market | Parcial | Docs de demo/seed | Alto | Handoff, demo script y checklist cliente |

## 5. Criterios de aceptacion 100%

Para declarar 100%, todos los puntos siguientes deben estar cerrados con evidencia:

- `makemigrations --check --dry-run` pasa sin cambios pendientes.
- `python manage.py check` pasa con settings de test y produccion-like.
- Tests backend MedSupplier pasan.
- `npm run lint` pasa.
- `npm run build` pasa.
- E2E MedSupplier pasa en flujo demo.
- Cliente no puede ver cockpit comercial privado.
- Cliente no puede ver margen, comisiones, adelantos, forecast privado ni notas internas.
- Logistica no puede ver margen/comisiones.
- Auditor read only no puede escribir.
- Usuario cross-tenant no accede datos ajenos.
- Serializers no exponen campos privados a roles cliente.
- Todos los endpoints requieren autenticacion y aplican permisos por objeto.
- Audit trail registra acciones criticas con razon, actor, tenant, account, IP/user-agent y correlation id.
- Document Room controla version vigente, obsolescencia y aprobacion.
- Quote tiene serializer publico, serializer privado y lineas de cotizacion.
- PO tiene lineas, vinculo a quote/account/item/lote/shipment.
- NCR/CAPA tiene aging, causa raiz, acciones, cierre y efectividad.
- FMEA existe o queda formalmente fuera de alcance MVP con roadmap tecnico aprobado.
- Evidence package/exportables MedSupplier existen.
- Compliance/validation package contiene artefactos reales: URS, FRS, SRS/TDS, risk assessment, traceability matrix, test plan, test cases y test evidence.

## 6. Backlog de remediacion

### P0 - Bloquea venta enterprise

1. Limpiar migraciones pendientes en `authentication` y `core`.
2. Reemplazar serializers `fields='__all__'` por serializers explicitos.
3. Crear matriz RBAC MedSupplier con roles Supplier/Customer/Auditor.
4. Implementar ABAC por organization, account, visibility, confidentiality, role y relacion customer/supplier.
5. Separar serializers/endpoints publicos y privados para cotizaciones y cockpit comercial.
6. Crear pruebas de privacidad comercial: cliente no ve margen/comisiones/notas internas.
7. Crear pruebas cross-tenant para recursos principales, no solo accounts.

### P1 - Necesario para MVP vendible controlado

1. Cockpit comercial privado basico.
2. QuoteLine y OrderLine.
3. Shipment milestones.
4. Document approvals formales.
5. Audit trail con reason/correlation_id/payload hash.
6. Exportable inicial de traceability package por account/order.
7. Dashboards por perfil: compras cliente, calidad cliente, comercial, quality, ops.
8. QA completo: backend tests, frontend build, lint y E2E.

### P2 - Enterprise regulated readiness

1. E-signature Part 11-ready.
2. EvidencePackage completo.
3. FMEA/FMEAItem.
4. CAPAAction y effectiveness verification formal.
5. AIInteractionLog MedSupplier con human review.
6. Validation package completo.
7. SOPs sugeridas y matriz de trazabilidad de requisitos.

## 7. Bitacora de comparacion

Cada avance debe agregarse aqui con evidencia.

| Fecha | Version/commit | Cumplimiento estimado | Cambios cerrados | QA ejecutado | Riesgo residual |
| ----- | -------------- | --------------------- | ---------------- | ------------ | --------------- |
| 2026-06-26 | Baseline local | 62% | CRUD/API/UI/audit inicial | `manage.py check` PASS, `npm run lint` PASS, `makemigrations --check` FAIL | RBAC/ABAC, privacidad comercial, migraciones |

## 8. Evidencia tecnica baseline

### Comandos ejecutados

```bash
pwd
ls -la /home/felipe/proyectos
ls -la /home/felipe/proyectos/ISO_Smart_MedSupplier
ls -la /home/felipe/proyectos/isosmart
ls -la /home/felipe/proyectos/adminapps
find ... estructura/codigo/docs/tests
rg ... autenticacion/permisos/tenant/audit/medsupplier
ISOSMART_LOG_DIR=/tmp/medsupplier-audit-logs DJANGO_SETTINGS_MODULE=backend.settings_test /home/felipe/proyectos/isosmart/backend/.venv312/bin/python manage.py check
ISOSMART_LOG_DIR=/tmp/medsupplier-audit-logs DJANGO_SETTINGS_MODULE=backend.settings_test /home/felipe/proyectos/isosmart/backend/.venv312/bin/python manage.py makemigrations --check --dry-run
ISOSMART_LOG_DIR=/tmp/medsupplier-audit-logs DJANGO_SETTINGS_MODULE=backend.settings_test /home/felipe/proyectos/isosmart/backend/.venv312/bin/python manage.py migrate --plan
npm run lint
```

### Resultados

- `manage.py check`: PASS, 0 issues.
- `migrate --plan`: PASS, no planned migration operations.
- `npm run lint`: PASS.
- `python -m pip check`: FAIL, el Python del venv documentado no tiene modulo `pip`.
- `makemigrations --check --dry-run`: FAIL, detecto:
  - `authentication/migrations/0010_alter_refreshtokenblacklist_token_hash.py`
  - `core/migrations/0020_alter_featureflag_id.py`

### Comandos no ejecutados en esta auditoria

- `npm install`: no ejecutado porque puede modificar dependencias.
- `npm run build`: no ejecutado porque escribe `frontend/dist`.
- `python manage.py test`: no ejecutado porque escribe base de pruebas.
- `npm run test:e2e:medsupplier`: no ejecutado porque siembra datos y genera artefactos Playwright.

## 9. Regla de actualizacion

Despues de cada bloque natural:

1. Actualizar la matriz `MS-*`.
2. Mover items P0/P1/P2 cerrados a la bitacora.
3. Registrar comandos QA ejecutados y resultado.
4. Ajustar porcentaje estimado solo con evidencia.
5. No marcar 100% mientras exista un P0 abierto.

