# Pilot Known Limitations - ISO Smart MedSupplier

Date: 2026-06-29

## Commercial Limitations

- Paid pilot is controlled in scope.
- Controlled enterprise MVP is allowed with restrictions.
- Live controlled production is not approved until target gates are complete.
- Full regulated production is not approved.
- Formal validation is not complete.
- Customer/company remains responsible for SOP approval, validation protocol, training, and regulated-use acceptance.

## Technical Limitations

- Final target SSL/domain verification is pending.
- Final target backup artifact and checksum are pending.
- Restore drill is pending.
- Rollback rehearsal or formal acceptance is pending.
- Monitoring activation is pending on final target.
- Human release approval is pending.
- Final staging/production target must repeat AdminApps no-fallback smoke.
- Binary PDF evidence export is future or buyer-specific scope.

## Product Boundary

- MedSupplier is separate from ISO Smart unless a joint package is explicitly scoped.
- ISO Smart frontend lint/E2E remediation is required before selling a joint ecosystem release.
- AdminApps remains the authority for organizations, users, entitlements, and billing/subscription state.
- Local fallback must not be used as production integration evidence.

## Data Limitations

- Standard pilot data must be synthetic, seeded, sanitized, or approved.
- Patient data and regulated production records are not allowed in the standard pilot.
- Real supplier/customer confidential data requires written approval.

## Support Limitations

- Standard pilot support is not 24/7 production support.
- Incident response applies only within contracted pilot scope.
- Infrastructure support applies only when explicitly contracted.

## Required Disclosure

Before the buyer signs or starts the pilot, disclose:

- what is approved,
- what is not approved,
- known target gates,
- data restrictions,
- support cadence,
- next decision criteria.
