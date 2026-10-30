# MedSupplier ISO Inheritance Review - 2026-06-27

| Elemento heredado | Tipo | Se mantiene | Se elimina | Justificacion | Riesgo |
| ----------------- | ---- | ----------- | ---------- | ------------- | ------ |
| `ai_modules.sca` | Django app ISO | Temporal | No | Forma parte del baseline heredado y puede ser requerido por settings/rutas existentes. | Acoplamiento funcional ISO; revisar antes de RC. |
| `ai_modules.sie` | Django app ISO | Temporal | No | Igual que SCA; no remover sin mapa de dependencias. | Dificulta lectura de producto independiente. |
| `ai_modules.asb` | Django app ISO | Temporal | No | Presente en `INSTALLED_APPS`; requiere evaluacion de imports/migraciones. | Puede arrastrar deuda no MedSupplier. |
| `ai_modules.spm` | Django app ISO | Temporal | No | Presente en baseline; mantener hasta separar core compartido. | Acoplamiento a procesos ISO. |
| `core.Organization` | Modelo tenant | Si | No | Base multi-tenant local usada por MedSupplier y tests. | Debe sincronizarse con AdminApps como autoridad. |
| `authentication.UserProfile` | Perfil/roles | Si | No | Se usa como fallback controlado de permisos y login local. | Fallback debe seguir deshabilitado en produccion real. |
| Textos "ISO Smart MedSupplier" | Marca/producto | Si | No | Nombre comercial actual del producto. | Evitar que implique que vive dentro de Iso Smart. |
| Subjects/email `[ISO Smart]` fuera de MedSupplier | Texto heredado | Temporal | No | Pertenece a modulos ISO heredados, no al dominio MedSupplier directo. | Puede confundir despliegues standalone. |
| Venv de `/isosmart/backend/.venv312` | Workaround local | No como contrato | Si como dependencia release | Se uso para validar por falta de venv propio. | Bloquea reproducibilidad si queda como contrato. |
