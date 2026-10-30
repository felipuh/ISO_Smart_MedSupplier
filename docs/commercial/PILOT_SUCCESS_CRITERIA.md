# Pilot Success Criteria - ISO Smart MedSupplier

Date: 2026-06-29

## Purpose

Define measurable criteria for deciding whether a MedSupplier paid pilot should stop, extend, move to controlled enterprise MVP, or prepare controlled production gates.

## Required Success Criteria

| Area | Success Criterion | Evidence |
| --- | --- | --- |
| Access authority | AdminApps controls organization/product access with no fallback in target smoke. | `check_medsupplier_adminapps --no-fallback` result. |
| Tenant isolation | Users see only scoped organization/account data. | Role smoke and E2E evidence. |
| Commercial privacy | Customer roles and non-finance supplier roles cannot access private cockpit or private financial fields. | E2E and API permission evidence. |
| Supplier workflow | Supplier account, document, quote, order/shipment, and quality flows are understandable to pilot users. | Pilot review notes. |
| Customer workflow | Customer roles can review scoped data without private supplier information. | Customer role walkthrough. |
| Evidence package | Buyer can review evidence package output and decide whether JSON/HTML export is sufficient for pilot. | Evidence package sample. |
| AdminApps billing/entitlement | Subscription and entitlement state can allow or deny access as expected. | AdminApps deny-safe evidence. |
| Support model | Weekly cadence and escalation owner are accepted. | Signed or acknowledged pilot support model. |
| Limitations | Buyer understands no regulated production claim is made. | Scope/limitations acknowledgement. |

## Optional Success Criteria

- Buyer identifies required integrations for a next phase.
- Buyer validates pilot data model against their supplier quality process.
- Buyer confirms which SOPs and validation protocol would be needed for regulated use.

## Failure Criteria

- AdminApps entitlement cannot be verified without fallback in the agreed target.
- Role/privacy controls fail.
- Buyer requires regulated production claims during pilot.
- Required data cannot be safely classified for pilot use.
- Support or scope ownership is not assigned.

## Decision Outcomes

- Stop: pilot criteria not met or buyer no longer has a valid use case.
- Extend: criteria partly met and scope remains controlled.
- Move to controlled enterprise MVP: criteria met and broader controlled workflow is justified.
- Prepare controlled production: only after target gates are completed separately.
