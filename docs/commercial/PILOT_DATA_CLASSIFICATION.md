# Pilot Data Classification - ISO Smart MedSupplier

Date: 2026-06-29

## Purpose

Define what data can be used during a MedSupplier pilot and what requires additional approval.

## Allowed By Default

- Synthetic supplier/customer names.
- Seeded demo data.
- Sanitized supplier account examples.
- Sanitized quality event examples.
- Sanitized RFQ/quote/order/shipment examples.
- Training-only documents with no confidential content.

## Requires Written Approval

- Real supplier names.
- Real customer names.
- Real quote or pricing examples.
- Real quality records.
- Real shipment or purchase order examples.
- Confidential supplier/customer documents.
- Production-like operational data.

## Not Allowed In Standard Pilot

- Patient data.
- Regulated production records.
- Secrets, API keys, passwords, tokens, private keys, certificates, or recovery codes.
- Data from organizations outside the contracted tenant.
- Data the buyer cannot classify or approve.

## Field Sensitivity

| Data Type | Sensitivity | Handling |
| --- | --- | --- |
| User names/emails | Internal/pilot | Use pilot-approved accounts only. |
| Supplier private financial fields | Confidential | Supplier finance/admin only; never customer-visible. |
| Customer account scope | Confidential | Enforce account-scoped views. |
| Quality event/CAPA details | Internal or confidential | Use sanitized examples unless approved. |
| Evidence packages | Internal or confidential | Export only approved pilot data. |
| Audit/e-signature records | Internal control evidence | Keep with pilot evidence package. |

## Buyer Responsibilities

- Classify pilot data before upload.
- Approve any real business data.
- Confirm data retention expectations.
- Confirm deletion/export expectations at pilot closeout.

## Product Responsibilities

- Enforce role and account scope.
- Hide private commercial fields from unauthorized roles.
- Keep audit trail evidence for pilot actions.
- Avoid logging secrets or confidential content.
