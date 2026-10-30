# ISO Smart MedSupplier Baseline Migration Fix - 2026-06-27

## Resumen

* Problema detectado: `makemigrations --check --dry-run` fallaba en el backend base por drift de migraciones.
* Comando que fallo: `DJANGO_SETTINGS_MODULE=backend.settings_test /home/felipe/proyectos/isosmart/backend/.venv312/bin/python manage.py makemigrations --check --dry-run --verbosity 3`.
* Migraciones pendientes: `authentication/migrations/0010_alter_refreshtokenblacklist_token_hash.py` y `core/migrations/0020_alter_featureflag_id.py`.
* Causa raiz: `authentication.RefreshTokenBlacklist.token_hash` declaraba `db_index=True` en el modelo pero no en el estado migrado; `core.FeatureFlag.id` heredaba `BigAutoField` por `DEFAULT_AUTO_FIELD` aunque la migracion historica `0019_featureflag` lo creo como `AutoField`.
* Decision tecnica: generar migracion controlada para `authentication.token_hash`; no alterar el tipo de PK de `FeatureFlag` y fijar explicitamente el `AutoField` historico en el modelo.
* Estado final: detector de migraciones restaurado (`No changes detected`). El baseline RC completo no queda aprobado por brechas preexistentes de comando/app/script y lint frontend.

## Migraciones revisadas

### authentication - RefreshTokenBlacklist.token_hash

* Cambio: `models.CharField(max_length=64, unique=True)` pasa a `models.CharField(max_length=64, unique=True, db_index=True)` en el estado de migraciones.
* Riesgo: bajo. El campo ya es unico y el hash SHA-256 ya tiene longitud 64; no hay cambio de datos ni exposicion de token raw.
* Decision: aceptar migracion schema/state controlada `0010_alter_refreshtokenblacklist_token_hash.py`.
* Evidencia: `migrate --plan` solo lista `authentication.0010_alter_refreshtokenblacklist_token_hash` con `Alter field token_hash`.

### core - FeatureFlag.id

* Cambio: Django queria alterar `FeatureFlag.id` de `AutoField` historico a `BigAutoField` por `CoreConfig.default_auto_field` y `DEFAULT_AUTO_FIELD`.
* Riesgo: medio si se acepta como migracion, porque altera una primary key. No se encontraron foreign keys hacia `FeatureFlag`, pero no habia evidencia de intencion funcional para cambiar el PK.
* Decision: no generar migracion de core; fijar `id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')` en `FeatureFlag`.
* Evidencia: despues del ajuste, `makemigrations --check --dry-run --verbosity 3` devuelve `No changes detected`.

## Archivos modificados

* `/home/felipe/proyectos/isosmart/backend/authentication/migrations/0010_alter_refreshtokenblacklist_token_hash.py`
* `/home/felipe/proyectos/isosmart/backend/core/models.py`
* `/home/felipe/proyectos/ISO_Smart_MedSupplier/docs/internal/MEDSUPPLIER_BASELINE_MIGRATION_FIX_2026-06-27.md`

## Comandos ejecutados

| Comando | Resultado | Observacion |
| ------- | --------- | ----------- |
| `git status --short` en backend base | FAIL/dirty | Habia cambios previos en `isosmart`; no fueron revertidos. |
| `manage.py check` | PASS | Sin issues. |
| `manage.py makemigrations --check --dry-run --verbosity 3` inicial | FAIL | Detecto `authentication.0010` y `core.0020`. |
| `find authentication/migrations` y `rg RefreshTokenBlacklist/token_hash` | PASS | Se confirmo campo `token_hash` y migracion previa `0004`. |
| `find core/migrations` y `rg FeatureFlag/DEFAULT_AUTO_FIELD` | PASS | Se confirmo `FeatureFlag.id` historico como `AutoField` y default global `BigAutoField`. |
| `manage.py makemigrations authentication core` | PASS | Genero migracion auth y, temporalmente, core; core se descarto al corregir modelo. |
| `manage.py makemigrations --check --dry-run --verbosity 3` final | PASS | `No changes detected`. |
| `manage.py migrate --plan` | PASS | Solo queda planificada `authentication.0010`. |
| `manage.py test authentication core medsupplier` | FAIL | `medsupplier` no existe como modulo Django importable. |
| `manage.py test authentication core` | PASS | 78 tests OK. |
| `manage.py test medsupplier` | FAIL | `ModuleNotFoundError: No module named 'medsupplier'`. |
| `manage.py check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e` | FAIL | Management command desconocido. |
| `npm run lint` | FAIL | 5 errores no relacionados: `t` sin uso y `process` no definido en `vite.config.js`. |
| `npm run build` | PASS | Build de Vite completado. |
| `npm run test:e2e:medsupplier` | FAIL | Script npm no existe. |
| `npm run` | PASS | Lista scripts disponibles; no incluye `test:e2e:medsupplier`. |
| `git status --short` en `ISO_Smart_MedSupplier` | PASS antes del doc | Repo limpio antes de crear este documento. |
| `git status --short` en `isosmart` | DIRTY | Incluye cambios previos y los cambios de esta correccion. |

## Riesgos restantes

* El baseline RC completo no puede declararse verde mientras `manage.py test medsupplier`, `check_medsupplier_adminapps`, `npm run lint` y `npm run test:e2e:medsupplier` fallen.
* El repo base `isosmart` ya tenia cambios sucios no relacionados antes de esta correccion.
* La migracion de authentication agrega `db_index=True` sobre un campo `unique=True`; en algunas bases puede ser redundante, pero refleja el modelo existente.

## Decision

* Baseline restaurado con observaciones.

## Proximo paso recomendado

No continuar con sprint RC Fase 1 a Fase 8 hasta resolver o justificar formalmente las brechas restantes de baseline completo.
