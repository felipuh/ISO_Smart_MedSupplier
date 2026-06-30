# AdminApps Real Smoke Evidence

Date: 2026-06-29 15:49 CST

## Objective

Close the P1 item requiring MedSupplier to validate product access against real AdminApps without local fallback.

This evidence does not accept fallback as a real integration pass.

## Root Cause

Initial no-fallback smoke failed because MedSupplier sent the local integer organization id to AdminApps:

```text
http://127.0.0.1:8000/api/integration/organizations/3/products/MEDSUPPLIER/validate/
```

AdminApps correctly exposes the product validation route with a UUID organization id:

```text
/api/integration/organizations/<uuid:org_id>/products/<str:product_code>/validate/
```

The target AdminApps database also had pending product-system migrations, so `product_systems` and `organization_product_entitlements` did not exist before remediation.

## Remediation Applied

AdminApps target:

- Applied pending migrations:
  - `subscriptions.0002_alter_plan_modules_included`
  - `products.0002_productsystem_organizationproductentitlement`
- Confirmed `ProductSystem` seed exists for `MEDSUPPLIER`.
- Seeded local target organization:
  - code: `MEDSUPDEMO`
  - id: `4d4e38a8-1f1b-4a2d-8295-0a7692a413ba`
  - status: `active`
- Seeded active subscription and active `MEDSUPPLIER` entitlement.
- Seeded deny-safe fixtures:
  - no entitlement organization: `1ae51bff-0c6c-4ea9-98f6-bd72e14435c9`
  - billing blocked organization: `ac31a310-4b1d-427f-99df-d17e6126d9c8`
  - suspended organization: `9dfe230f-d5fe-4269-84f8-60106d9f7f3e`

MedSupplier local test target:

- Mapped `core.Organization(slug='medsupplier-demo-e2e').external_id` to AdminApps UUID:

```text
4d4e38a8-1f1b-4a2d-8295-0a7692a413ba
```

Code hardening:

- `check_medsupplier_adminapps` supports `--no-fallback`.
- `AdminAppsClient.validate_product_access()` supports per-call `allow_local_fallback`.
- AdminApps integration requests send configurable `X-Forwarded-Proto`, defaulting to `https`, so direct local gunicorn smoke can match the deployed proxy contract.

## Configuration Used

MedSupplier repository:

```bash
/home/felipe/proyectos/ISO_Smart_MedSupplier/backend
```

AdminApps target:

```text
http://127.0.0.1:8000/api/integration
```

Settings:

```bash
DJANGO_SETTINGS_MODULE=backend.settings_test
```

Fallback allowed: no.

Smoke command:

```bash
DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check_medsupplier_adminapps \
  --organization-slug medsupplier-demo-e2e \
  --no-fallback
```

Final AdminApps endpoint used:

```text
http://127.0.0.1:8000/api/integration/organizations/4d4e38a8-1f1b-4a2d-8295-0a7692a413ba/products/MEDSUPPLIER/validate/
```

## Positive Smoke Result

Command output:

```text
organization=3 slug=medsupplier-demo-e2e
adminapps_available=True
fallback_allowed=False
product_access_source=adminapps
medsupplier_entitlement_enabled=True
medsupplier_access_reason=ok
active_medsupplier_scopes=10
MedSupplier AdminApps smoke passed.
```

Decision: PASS real without fallback.

## Deny-Safe Evidence

| Case | Endpoint / Condition | Result | Observation |
| --- | --- | --- | --- |
| No entitlement | Active org without `MEDSUPPLIER` entitlement | HTTP 403 | `allowed=false`, `reason=product_not_enabled`. |
| Billing blocked | Active org, entitlement enabled, subscription `past_due` | HTTP 403 | `allowed=false`, `reason=billing_blocked`, `billing_status=past_due`. |
| Suspended org | Suspended organization with entitlement | HTTP 404 | `allowed=false`, `code=organization_not_found`; inactive org is not accepted as valid authority target. |
| Missing API key | Valid org without `X-API-Key` | HTTP 401 | `code=missing_api_key`. |

No local fallback was accepted in any deny-safe case.

## Regression Evidence

| Repo | Command | Result | Observation |
| --- | --- | --- | --- |
| AdminApps backend | `DJANGO_SETTINGS_MODULE=config.settings BILLING_SCHEDULER_ENABLED=false ./.venv312/bin/python manage.py check` | PASS | No issues. |
| AdminApps backend | `DJANGO_SETTINGS_MODULE=config.settings BILLING_SCHEDULER_ENABLED=false ./.venv312/bin/python manage.py migrate --plan` | PASS | No planned migration operations after remediation. |
| AdminApps backend | `DJANGO_SETTINGS_MODULE=config.settings_test BILLING_SCHEDULER_ENABLED=false ./.venv312/bin/python manage.py test apps.products apps.billing apps.users apps.api` | PASS | 123 tests OK. |
| MedSupplier backend | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py test medsupplier` | PASS | 47 tests OK, including no-fallback command tests. |
| MedSupplier backend | `DJANGO_SETTINGS_MODULE=backend.settings_test ./.venv312/bin/python manage.py check_medsupplier_adminapps --organization-slug medsupplier-demo-e2e --no-fallback` | PASS | Real AdminApps target validation, no fallback. |

## Decision

AdminApps real smoke: PASS.

P1 status: CLOSED for local target integration evidence.

Remaining limitation:

- Repeat the same no-fallback smoke in the final staging/production target before controlled production approval.

Controlled production status: NOT APPROVED YET because SSL/domain, backup artifact/checksum, restore drill, rollback rehearsal, monitoring activation, and human approval remain separate target-environment gates.
