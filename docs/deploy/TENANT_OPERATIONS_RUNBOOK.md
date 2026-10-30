# Tenant Operations Runbook

Date: 2026-06-29

Scope: demo tenant and controlled customer tenant setup for ISO Smart MedSupplier.

## Tenant Types

| Type | Purpose | Data Allowed |
| --- | --- | --- |
| Demo tenant | Buyer walkthroughs and internal demos. | Seeded or approved non-sensitive data only. |
| Pilot tenant | Paid pilot or POC with agreed success criteria. | Approved pilot data within written scope. |
| Controlled customer tenant | Production-like non-regulated operation. | Customer-approved data only after environment, support, and backup controls are accepted. |

## Preconditions

- AdminApps organization exists.
- AdminApps product entitlement for `MEDSUPPLIER` is enabled.
- Billing or subscription state is active for the agreed scope.
- MedSupplier local fallback is disabled outside test settings.
- Customer data classification is approved.
- Support owner and escalation path are named.

## Demo Tenant Setup

1. Use the approved demo organization slug.
2. Seed demo users and sample MedSupplier data.
3. Confirm users cover the expected role matrix:
   - Supplier admin/manager.
   - Supplier finance.
   - Supplier quality/logistics.
   - Supplier viewer.
   - Customer quality/procurement/viewer.
4. Run E2E demo smoke:

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier/frontend
npm run test:e2e:medsupplier
```

5. Reset or reseed demo data after buyer sessions if the dataset was modified.

## Pilot Tenant Setup

1. Create or confirm AdminApps organization.
2. Enable `MEDSUPPLIER` product entitlement.
3. Confirm subscription/billing status with the commercial owner.
4. Create approved user accounts and roles.
5. Configure MedSupplier account/customer scope.
6. Confirm customer-facing roles cannot access supplier-private financial fields.
7. Run AdminApps entitlement smoke:

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier
backend/.venv312/bin/python backend/manage.py check_medsupplier_adminapps --organization-slug <pilot-org-slug> --settings=backend.settings
```

8. Attach onboarding checklist and support model to the pilot record.

## Controlled Operation Checklist

- [ ] `DEBUG=False`.
- [ ] HTTPS active.
- [ ] `/health` and `/ready` return 200.
- [ ] AdminApps integration smoke returns allowed for entitled pilot tenant.
- [ ] Backup schedule active.
- [ ] Restore drill evidence completed or explicitly accepted as a pre-go-live gap.
- [ ] Rollback command path reviewed.
- [ ] Support owner assigned.
- [ ] Known issues reviewed with pilot owner.
- [ ] Scope and limitations acknowledged.

## Tenant Suspension

If AdminApps marks a product entitlement inactive, past due, suspended, or unavailable:

- MedSupplier must deny product access.
- Do not enable local fallback as a commercial workaround.
- Record support ticket, tenant, reason, operator, and resolution.

## Offboarding

1. Confirm commercial closure or pilot completion.
2. Disable AdminApps product entitlement.
3. Disable or remove user access according to agreement.
4. Export approved evidence if contracted.
5. Confirm data retention or deletion instruction.
6. Record final backup status and offboarding approval.

