# Risk Assessment

| Risk | Control |
| --- | --- |
| Customer sees Supplier private pricing | Serializer field filtering, visibility taxonomy, account scope tests |
| Cross-tenant data exposure | Organization-scoped querysets and object checks |
| Unauthorized workflow approval | Domain role checks and e-signature reason requirement |
| Incomplete evidence package exported | Backend validation blocks empty package export |
| Audit trail tampering | Event hash and previous hash chain for audit-ready review |
