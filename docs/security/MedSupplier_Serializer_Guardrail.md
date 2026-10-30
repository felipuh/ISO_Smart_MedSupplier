# MedSupplier Serializer Guardrail

Fecha: 2026-06-26

El módulo MedSupplier usa un guardrail automatizado en `backend/medsupplier/tests.py`.

Controles:

- Falla si un `ModelSerializer` de `backend/medsupplier/serializers.py` usa `fields = "__all__"`.
- Falla si un serializer MedSupplier no declara `Meta.fields` explícito.
- Falla si el catálogo `PRIVATE_COMMERCIAL_FIELDS` pierde campos privados comerciales críticos.

Campos privados protegidos:

- `private_margin_notes`
- `supplier_cost`
- `margin`
- `commission`
- `advance`
- `internal_notes`
- `pricing_internal`
- `private_notes`
- `supplier_private_notes`
- `internal_cost`
- `internal_price`
- `forecast_private`

Ejecución:

```bash
DJANGO_SETTINGS_MODULE=backend.settings_test /home/felipe/proyectos/isosmart/backend/.venv312/bin/python manage.py test medsupplier
```
