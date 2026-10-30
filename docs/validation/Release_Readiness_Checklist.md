# Release Readiness Checklist

Date: 2026-06-29

This checklist supports a validation-ready and audit-ready release review. It does not replace formal customer/company validation, SOP approval, training, or regulated production release authorization.

- [x] Backend checks pass.
- [x] Migration dry-run reports no pending changes.
- [x] MedSupplier tests pass.
- [x] Frontend lint passes.
- [x] Frontend build passes.
- [x] MedSupplier E2E completed.
- [x] No sensitive MedSupplier serializers use `fields="__all__"`.
- [x] Customer privacy tests pass.
- [x] Endpoint/role matrix evidence exists.
- [x] AdminApps product authority tests pass.
- [x] Production-like hardening documented.
- [x] CI/CD pipelines defined.
- [x] Rollback plan documented.
- [x] Backup/restore runbook documented.
- [x] Known issues documented.
- [x] Compliance language reviewed for prohibited claims.
- [ ] Restore drill executed in staging.
- [ ] Human review approval signed.
- [ ] Customer/company validation protocol approved.
