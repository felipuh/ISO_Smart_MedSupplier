# Security Notes

## Controles heredados

- Autenticación JWT/SSO Smart3AI.
- AdminApps como autoridad central de identidad, organizaciones, usuarios, roles y entitlements.
- Modelo de usuario central `authentication.User`.
- Membresías por organización con `authentication.UserProfile`.
- Throttling DRF.
- Headers y cookies endurecidas en settings base.
- CORS/CSRF configurables por ambiente.

## Controles específicos MedSupplier

- Todos los viewsets requieren autenticación.
- El middleware de módulos valida que AdminApps tenga habilitado `MEDSUPPLIER` para la organización activa.
- Todos los registros operativos incluyen `organization`.
- Las APIs verifican membresía activa contra `UserProfile`.
- Escritura permitida solo a `org_admin`, `iso_manager` y `user`.
- `auditor` y `viewer` quedan en lectura.
- Relaciones cross-tenant se rechazan en serializers.
- Audit events del módulo quedan previstos para eventos regulados y exportables.
