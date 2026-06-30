# Pilot Demo Script - ISO Smart MedSupplier

Date: 2026-06-29

## Setup

- Use seeded demo data or buyer-approved pilot data.
- Confirm AdminApps organization and `MEDSUPPLIER` entitlement.
- Run no-fallback AdminApps smoke before the session when possible.
- Confirm supplier and customer demo users.
- Confirm no regulated production data is used.

## Opening

Position MedSupplier as a controlled supplier/customer workspace for pilot evaluation.

Say:

- AdminApps controls organizations, users, product access, entitlement, and subscription/billing state.
- MedSupplier controls supplier/customer operational workflows.
- The pilot is validation-ready and audit-ready, but formal validation remains the customer/company responsibility.

Do not say:

- The system is formally validated.
- The system is approved for regulated production.
- The pilot replaces SOPs, training, or customer/company quality system controls.

## Flow

1. AdminApps authority
   - Explain tenant, users, entitlement, subscription/billing dependency.
   - Mention no-fallback smoke evidence.

2. Supplier Admin workspace
   - Show accounts.
   - Create or review a supplier/customer account.
   - Show role and account scope concept.

3. Documents
   - Show controlled document list.
   - Show approval or obsolescence pattern.
   - Explain audit/e-signature evidence.

4. RFQ and quote
   - Open RFQ/quote.
   - Show supplier-private fields.
   - Explain customer-safe view.

5. Orders and shipments
   - Show purchase order and shipment/lot traceability.
   - Explain inspection and delivery evidence.

6. Quality
   - Show NCR/CAPA/FMEA surfaces.
   - Explain closure evidence and effectiveness review concept.

7. Evidence package
   - Show package index and export-ready evidence.
   - Explain JSON/HTML support and PDF as future or buyer-specific scope.

8. Customer role
   - Switch to customer user.
   - Confirm scoped account data.
   - Confirm private cockpit denied.
   - Confirm mutation denied where read-only.

## Close

Review success criteria, known limitations, support cadence, and next decision:

- stop,
- extend pilot,
- controlled enterprise MVP,
- prepare controlled production gates.
