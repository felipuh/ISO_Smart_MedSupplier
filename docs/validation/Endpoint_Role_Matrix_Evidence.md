# Endpoint Role Matrix Evidence

Date: 2026-06-29

## Source

- Matrix: `docs/internal/MEDSUPPLIER_ENDPOINT_ROLE_MATRIX.md`
- Executable tests: `MedSupplierEndpointRoleMatrixTests`

## Covered Roles

- Supplier Admin
- Supplier Sales
- Supplier Finance
- Supplier Quality
- Supplier Logistics
- Supplier Viewer
- Customer Admin
- Customer Buyer
- Customer Quality
- Customer Logistics
- Customer Auditor
- Customer Viewer

## Covered Endpoint Families

- Accounts
- Dashboard summary
- Effective permissions
- Quotes
- Purchase orders
- Shipments
- Documents
- CAPAs
- FMEAs
- Evidence packages
- Audit events
- Integration status
- Private cockpit

## Evidence

The Stage 10 backend evidence includes MedSupplier role matrix tests as part of:

```bash
backend/.venv312/bin/python backend/manage.py test core.tests.ProductionLikeProbeTests medsupplier --settings=backend.settings_test
```

Result: PASS, 48 tests.
