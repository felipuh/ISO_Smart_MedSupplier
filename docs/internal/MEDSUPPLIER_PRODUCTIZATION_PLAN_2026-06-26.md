# MedSupplier Productization Plan - 2026-06-26

## Estado ejecutivo

ISO Smart MedSupplier tiene backend, modelo de datos, APIs REST, seguridad por organizacion y pantallas de consulta. Todavia no esta listo para venta operacional porque el frontend no permite capturar, editar ni cerrar registros del flujo Supplier-Customer.

La prioridad deja de ser cosmetica o lint aislado. El foco inmediato es convertir el workspace en un producto usable por operaciones, calidad, supply chain y customer-facing teams.

## Criterio de producto vendible

Cada modulo operativo debe cumplir:

1. Captura desde UI con campos reales del modelo.
2. Edicion controlada desde UI.
3. Eliminacion o cierre segun criticidad regulada.
4. Validaciones minimas visibles.
5. Mensajes claros de error del backend.
6. Filtrado por organizacion activa.
7. Respeto de visibilidad `shared` / `private`.
8. QA con build, lint y prueba manual de flujo principal.

## Datos demo y QA funcional

Comando disponible:

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier
/home/felipe/proyectos/isosmart/backend/.venv312/bin/python backend/manage.py seed_medsupplier_demo --organization-slug medsupplier-demo
```

Este comando crea un workspace demo Supplier-Customer con cuenta regulada, cuenta privada, contacto, reunion, accion, requisito, documento, version documental, RFQ, cotizacion, PO, lote, shipment, inspeccion, NCR, CAPA y scorecard.

Tambien crea o actualiza un usuario demo:

- Email: `medsupplier.demo@smart3ai.local`
- Password inicial: `MedSupplierDemo@123`
- Rol: `iso_manager`

Para validarlo en entorno de QA SQLite:

```bash
/home/felipe/proyectos/isosmart/backend/.venv312/bin/python backend/manage.py migrate --settings=backend.settings_test --noinput
/home/felipe/proyectos/isosmart/backend/.venv312/bin/python backend/manage.py seed_medsupplier_demo --settings=backend.settings_test --organization-slug medsupplier-demo-qa
```

QA funcional en navegador:

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier/frontend
npm run test:e2e:medsupplier
```

Este E2E siembra la organizacion `medsupplier-demo-e2e`, entra por el formulario real de login, valida datos demo, crea una cuenta desde UI y comprueba acciones bloqueadas en documentos/cotizaciones.

Nota de ejecucion local: cuando AdminApps no autoriza usuarios demo, el login de navegador requiere iniciar Vite con `VITE_LOCAL_AUTH_BYPASS=1` y el backend con `ALLOW_LOCAL_AUTH_BYPASS_FOR_TESTS=True`. El bypass solo debe usarse para QA/demo local; el backend sigue validando credenciales locales, lockout de cuenta y perfil activo.

Si un usuario sincronizado desde AdminApps aparece localmente con password no usable, regenerar solo la contraseña local de desarrollo con:

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier
/home/felipe/proyectos/isosmart/backend/.venv312/bin/python backend/manage.py set_local_dev_password --email felipe@smart3ai.com --generate --confirm-local
```

El comando no cambia la contraseña de AdminApps. Solo habilita acceso local, limpia lockout y requiere `--confirm-local` cuando el entorno parece production-like.

## Reglas reguladas iniciales

- Los cambios creados desde APIs MedSupplier generan `MedSupplierAuditEvent` automaticamente.
- Se auditan creacion, actualizacion y eliminacion con usuario, IP, user-agent, record type, record id, valores anteriores y nuevos.
- Roles operativos (`org_admin`, `iso_manager`, `user`) pueden ver registros `shared` y `private`.
- Roles de solo lectura iniciales ven solo registros `shared`.
- `private` queda reservado para pipeline comercial, margen, forecast y notas internas.

## Workflows regulados implementados

Acciones disponibles desde API y UI:

- Cliente 360: generar QBR / scorecard.
- Document Room: aprobar documento como vigente.
- RFQ: marcar como enviada.
- Cotizaciones: aprobar o rechazar.
- Ordenes: cerrar PO.
- Calidad: cerrar evento de calidad.
- CAPA: cerrar CAPA.

Cada accion de workflow registra auditoria de cambio de estado y refresca el workspace.
Las acciones no aplicables se muestran deshabilitadas con razon visible en tooltip, para que el usuario entienda por que no puede ejecutarlas.

Reglas bloqueantes vigentes:

- No se puede aprobar un documento obsoleto.
- No se puede reenviar una RFQ ya enviada/cotizada/cerrada/cancelada.
- No se puede aprobar una cotizacion expirada.
- No se puede aprobar o rechazar una cotizacion ya aprobada/rechazada/expirada.
- No se puede cerrar una PO ya cerrada/cancelada.
- No se puede cerrar un evento de calidad con CAPA abierta.
- No se puede cerrar una CAPA sin resultado de efectividad.
- No se puede cerrar una CAPA ya cerrada/cancelada.

## Secuencia de implementacion

1. Cliente 360
   - Crear, editar y eliminar cuentas Supplier-Customer.
   - Base obligatoria para contactos, reuniones, requisitos, documentos, RFQ, PO y calidad.

2. Contactos
   - Capturar contactos por cuenta.
   - Distinguir contacto cliente/proveedor e inactivo/activo.

3. Reuniones y acciones
   - Registrar reuniones, minutas, decisiones y acciones.
   - Permitir seguimiento por responsable y fecha de vencimiento.

4. Requisitos
   - Capturar requisitos de cliente, regulatorios y tecnicos.
   - Preparar relacion con RFQ y documentos.

5. Document Room
   - Crear documentos controlados.
   - Agregar versiones y metadatos de aprobacion.

6. RFQ y cotizaciones
   - Crear RFQ.
   - Registrar cotizaciones y notas privadas.

7. Ordenes, lotes y shipments
   - Capturar PO, lotes y entregas.
   - Conectar estado logistico con cuentas y calidad.

8. Inspecciones, eventos de calidad y CAPA
   - Registrar inspecciones.
   - Abrir NCR, quejas, desviaciones y hallazgos.
   - Crear CAPA con causa raiz, acciones y verificacion.

9. Scorecards y QBR
   - Capturar desempeno por periodo.
   - Preparar vista ejecutiva para revision trimestral.

10. Datos demo y habilitacion comercial
    - Seed de workspace demo MedTech.
    - Guion de demo.
    - Checklist de venta/implementacion.

## Ciclo QA por tarea

Para cada tarea:

1. Implementar el flujo minimo completo.
2. Ejecutar `npm run build`.
3. Ejecutar `npm run lint`.
4. Ejecutar `python manage.py check --settings=backend.settings_test` con el venv correcto.
5. Ejecutar pruebas backend afectadas.
6. Corregir errores.
7. Repetir QA.
8. Documentar resultado y avanzar a la siguiente tarea.

## Estado de avance

- 2026-06-26: Plan creado.
- 2026-06-26: CRUD frontend de Cliente 360 implementado y validado.
- 2026-06-26: CRUD frontend de Contactos implementado y validado con selector de cuenta.
- 2026-06-26: CRUD frontend de Reuniones y Acciones implementado y validado con relaciones a cuenta/reunion.
- 2026-06-26: CRUD frontend de Requisitos, Document Room, versiones documentales con archivo opcional, RFQ, Cotizaciones, Ordenes, Lotes, Shipments, Inspecciones, Calidad, CAPA y Scorecards implementado y validado.
- 2026-06-26: Audit trail automatico, regla inicial de visibilidad `shared/private`, pruebas de permisos/auditoria y comando `seed_medsupplier_demo` implementados y validados.
- 2026-06-26: Workflows explicitos implementados y validados: aprobar documento, enviar RFQ, aprobar/rechazar cotizacion, cerrar PO, cerrar NCR/CAPA y generar QBR.
- 2026-06-26: Reglas bloqueantes por estado y usuario demo de QA/comercial agregados y validados.
- 2026-06-26: QA funcional end-to-end MedSupplier agregado con Playwright; se corrigio el proxy Vite hacia backend MedSupplier local y el mapa de acciones UI para que cada workflow aparezca solo en su modulo correcto.
- 2026-06-26: Acceso local/demo formalizado con `set_local_dev_password` para usuarios sincronizados desde AdminApps con password local no usable.
- Siguiente trabajo activo: ampliar guion de demo comercial con escenarios por rol, export/evidencia y checklist de handoff para implementacion cliente.
