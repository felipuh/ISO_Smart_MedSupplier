# MedSupplier AdminApps Smoke

Fecha: 2026-06-26

Comando:

```bash
/home/felipe/proyectos/isosmart/backend/.venv312/bin/python manage.py check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e
```

El smoke valida:

- Disponibilidad de AdminApps cuando el servicio externo responde.
- Resolución de módulos de la organización.
- Entitlement `MEDSUPPLIER` habilitado.
- Existencia de scopes MedSupplier activos.
- Fallback local controlado cuando AdminApps no está disponible.

Regla de seguridad:

El fallback local no abre permisos globales ni convierte usuarios en administradores. El acceso runtime continúa limitado por `MedSupplierUserScope`, `organization_id`, `account_scope`, `side` y `role`.
