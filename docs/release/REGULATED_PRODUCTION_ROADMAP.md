# Regulated Production Roadmap

Date: 2026-06-29

Scope:
- Future full regulated production readiness for ISO Smart MedSupplier.
- MedSupplier, AdminApps authority, hosting environment, operational controls, validation package, security, support, and customer/company approval process.

This roadmap does not approve regulated production use. It defines the work, evidence, reviews, and approvals required before any regulated production claim or broad customer rollout.

## Current Position

Current release stage:
- Release Candidate: conditional go for controlled review.
- Controlled production: prepared with pre-go-live conditions.
- Regulated production: future roadmap only.

Allowed positioning today:
- Controlled demo.
- Paid pilot.
- Proof of concept.
- Controlled enterprise MVP.
- Production-like non-regulated operation after environment approval.
- Validation-ready and audit-ready review package.

Not allowed today:
- Formal validation claim.
- Regulated production approval claim.
- Broad customer production rollout without signed approval.
- Regulatory compliance claim that has not been independently validated by the responsible organization.

## Roadmap Overview

| Phase | Objective | Exit Gate |
| --- | --- | --- |
| 1. Governance Setup | Define owners, scope, quality system interface, and approval authority. | Validation governance charter approved. |
| 2. Requirements Baseline | Freeze regulated-use scope, intended use, tenant model, and risk boundaries. | URS/SRS/FRS/TDS baselined and signed. |
| 3. Validation Planning | Approve validation plan, traceability, test protocols, and acceptance criteria. | Validation plan and protocol set approved. |
| 4. Controlled Evidence Execution | Execute IQ/OQ/PQ or equivalent validation evidence. | All planned protocols executed and deviations resolved or accepted. |
| 5. Security And Privacy Assurance | Complete security audit, pen test, threat review, and privacy review. | Critical/high issues remediated or formally accepted. |
| 6. Operational Qualification | Validate monitoring, backups, restore, rollback, DR, support, and change control. | Operations readiness package signed. |
| 7. Training And SOP Approval | Approve SOPs and train admins/operators/users. | Training records and SOP approvals complete. |
| 8. Legal/Regulatory Review | Review claims, contracts, data processing, and regulated-use language. | Legal/regulatory approval signed. |
| 9. Executive Release Approval | Final release board decision. | Executive go/no-go signed. |
| 10. Post-Go-Live Control | Monitor controlled operation, incidents, changes, and periodic review. | Periodic review cadence active. |

## Phase 1 - Governance Setup

Required work:
- Name release owner, product owner, validation owner, security owner, operations owner, support owner, and customer approval owner.
- Define intended regulated-use scope and explicit exclusions.
- Define whether the customer quality system, Smart3AI quality process, or a joint process owns each approval.
- Define acceptance criteria for production regulated readiness.
- Define document control process and change approval workflow.

Required artifacts:
- Governance charter.
- RACI matrix.
- Approval authority matrix.
- Regulated-use scope statement.
- Document control procedure.

Exit criteria:
- Owners named.
- Approval authority signed.
- Scope and exclusions signed.

## Phase 2 - Requirements Baseline

Required work:
- Freeze intended use.
- Freeze tenant/data boundaries.
- Freeze AdminApps dependency model.
- Freeze role matrix and customer/supplier data visibility rules.
- Review open known issues and classify which are blockers.
- Confirm traceability from requirements to tests and risk controls.

Required artifacts:
- Updated URS.
- Updated SRS.
- Updated FRS.
- Updated TDS.
- Updated traceability matrix.
- Updated risk assessment.
- Known issues disposition.

Existing inputs:
- `docs/validation/URS.md`
- `docs/validation/SRS.md`
- `docs/validation/FRS.md`
- `docs/validation/TDS.md`
- `docs/validation/Traceability_Matrix.md`
- `docs/release/KNOWN_ISSUES.md`

Exit criteria:
- Baseline documents reviewed and signed.
- Requirements changes frozen for validation execution.

## Phase 3 - Validation Planning

Required work:
- Approve validation strategy.
- Define IQ/OQ/PQ or equivalent protocol set.
- Define required test data.
- Define deviation handling.
- Define retest rules.
- Define evidence retention.
- Define human approval workflow.

Required artifacts:
- Validation master plan or equivalent.
- IQ protocol or equivalent environment qualification protocol.
- OQ protocol or equivalent functional/operational protocol.
- PQ protocol or equivalent user/workflow qualification protocol.
- Deviation log template.
- Test evidence template.
- Human approval package.

Existing inputs:
- `docs/validation/Test_Plan.md`
- `docs/validation/Test_Evidence_Template.md`
- `docs/validation/Human_Review_Approval_Template.md`
- `docs/validation/SOP_Suggestions.md`

Exit criteria:
- Protocols approved before execution.
- Acceptance criteria and deviation process signed.

## Phase 4 - Controlled Evidence Execution

Required work:
- Execute backend checks and tests under approved environment.
- Execute frontend lint/build checks under approved environment.
- Execute E2E flows using approved test data.
- Execute endpoint/role matrix tests.
- Execute AdminApps entitlement, billing, suspension, and product access tests.
- Execute tenant isolation tests.
- Execute evidence package generation and review.
- Record deviations and retests.

Required artifacts:
- Completed IQ/OQ/PQ or equivalent evidence.
- Test run logs.
- E2E evidence.
- Endpoint/role matrix evidence.
- AdminApps integration evidence.
- Deviation and retest log.
- Final validation summary report.

Existing inputs:
- `docs/validation/Test_Evidence.md`
- `docs/validation/E2E_Evidence.md`
- `docs/validation/Endpoint_Role_Matrix_Evidence.md`
- `docs/validation/AdminApps_Integration_Decision.md`
- `docs/validation/MEDSUPPLIER_ADMINAPPS_SMOKE.md`

Exit criteria:
- All critical and high validation deviations closed or formally accepted.
- Final validation summary signed.

## Phase 5 - Security And Privacy Assurance

Required work:
- Complete security architecture review.
- Complete dependency vulnerability review.
- Complete secret scanning.
- Complete OWASP ASVS review.
- Complete pen test or independent security test.
- Complete privacy/data classification review.
- Confirm audit trail expectations and log retention.
- Confirm no sensitive secrets or regulated customer content is logged.

Required artifacts:
- Security assessment report.
- Pen test report.
- Vulnerability remediation log.
- Secret scanning evidence.
- Privacy/data classification decision.
- Security signoff.

Existing inputs:
- `docs/security/OWASP_ASVS_L2_Checklist.md`
- `docs/security/Data_Classification.md`
- `docs/security/Privacy_Model.md`
- `docs/security/PRODUCTION_LIKE_HARDENING.md`
- `docs/deploy/MONITORING_LOGGING_RUNBOOK.md`

Exit criteria:
- No unresolved critical/high security finding unless formally accepted by authorized owner.
- Security and privacy signoff complete.

## Phase 6 - Operational Qualification

Required work:
- Configure production monitoring and alerting.
- Execute backup job and record artifact checksum.
- Execute restore drill into isolated target/staging environment.
- Execute rollback rehearsal or approved rollback tabletop.
- Define disaster recovery objectives.
- Confirm systemd/Nginx or selected deployment architecture.
- Confirm TLS/domain/proxy headers/CORS/CSRF.
- Confirm AdminApps target connectivity.
- Confirm support queue and incident response path.

Required artifacts:
- Monitoring evidence.
- Backup evidence.
- Restore drill evidence.
- Rollback rehearsal evidence.
- DR plan.
- Deployment checklist.
- Support readiness signoff.

Existing inputs:
- `docs/deploy/DEPLOYMENT_RUNBOOK.md`
- `docs/deploy/BACKUP_RESTORE_RUNBOOK.md`
- `docs/deploy/ROLLBACK_PLAN.md`
- `docs/deploy/MONITORING_LOGGING_RUNBOOK.md`
- `docs/deploy/TENANT_OPERATIONS_RUNBOOK.md`
- `docs/validation/Backup_Restore_Evidence.md`

Exit criteria:
- Restore drill passed.
- Rollback path approved.
- Monitoring and alerting active.
- DR targets accepted.

## Phase 7 - Training And SOP Approval

Required work:
- Approve SOPs for access management, change control, incident response, backup/restore, validation evidence, customer onboarding, and release approval.
- Train internal operators.
- Train pilot/customer admins.
- Train support team.
- Record training completion.

Required artifacts:
- Approved SOPs.
- Training materials.
- Training attendance/completion records.
- Role-specific operation manual.

Existing inputs:
- `docs/validation/SOP_Suggestions.md`
- `docs/internal/manual-operacion-por-roles.md`
- `docs/commercial/ONBOARDING_CHECKLIST.md`
- `docs/commercial/SUPPORT_MODEL_DRAFT.md`

Exit criteria:
- SOPs approved.
- Required training records complete.

## Phase 8 - Legal And Regulatory Review

Required work:
- Review product claims.
- Review sales language.
- Review customer contract language.
- Review data processing and privacy obligations.
- Review regulated-use responsibility boundaries.
- Confirm that validation responsibility and approval authority are explicit.

Required artifacts:
- Legal review memo.
- Regulatory review memo.
- Approved external language.
- Contract or pilot addendum.
- Customer acceptance record.

Existing inputs:
- `docs/compliance/Allowed_Language.md`
- `docs/compliance/Forbidden_Claims.md`
- `docs/compliance/COMPLIANCE_READY_STATEMENT.md`
- `docs/commercial/SCOPE_AND_LIMITATIONS.md`
- `docs/commercial/SALES_FAQ.md`

Exit criteria:
- Legal/regulatory approval signed.
- Customer-facing language approved.

## Phase 9 - Executive Release Approval

Required work:
- Compile release board package.
- Review validation summary.
- Review security report.
- Review operations readiness.
- Review legal/regulatory approvals.
- Review known issues and residual risks.
- Decide go/no-go.

Required artifacts:
- Executive release package.
- Final known issues and risk acceptance log.
- Signed go/no-go decision.
- Production release notes.
- Rollback and communication plan.

Existing inputs:
- `docs/release/RELEASE_CANDIDATE_REPORT.md`
- `docs/release/CONTROLLED_PRODUCTION_READINESS_REPORT.md`
- `docs/release/RELEASE_NOTES.md`
- `docs/release/CHANGE_LOG.md`
- `docs/release/KNOWN_ISSUES.md`

Exit criteria:
- Executive approval signed.
- Release owner authorizes regulated production start.

## Phase 10 - Post-Go-Live Control

Required work:
- Monitor daily during initial go-live window.
- Review incidents and deviations.
- Track production changes through formal change control.
- Perform periodic access reviews.
- Perform backup/restore verification on schedule.
- Review audit trail and logs according to SOP.
- Maintain release notes and validation impact assessment for changes.

Required artifacts:
- Go-live monitoring log.
- Incident/deviation records.
- Change control records.
- Access review records.
- Backup/restore periodic evidence.
- Periodic management review.

Exit criteria:
- Stable operation through agreed hypercare period.
- Ongoing control cadence active.

## Mandatory Go/No-Go Checklist

Before regulated production can be approved:

- [ ] Governance charter signed.
- [ ] Intended use and exclusions signed.
- [ ] URS/SRS/FRS/TDS baselined and signed.
- [ ] Traceability matrix complete.
- [ ] Risk assessment reviewed and accepted.
- [ ] Validation plan approved.
- [ ] IQ/OQ/PQ or equivalent protocols approved.
- [ ] IQ/OQ/PQ or equivalent protocols executed.
- [ ] Deviations closed or accepted.
- [ ] Human approval package signed.
- [ ] SOPs approved.
- [ ] Training complete.
- [ ] Security audit complete.
- [ ] Pen test complete.
- [ ] Critical/high security findings closed or accepted.
- [ ] Secret scanning evidence complete.
- [ ] Backup evidence complete.
- [ ] Restore drill passed.
- [ ] Disaster recovery plan approved.
- [ ] Monitoring and alerting active.
- [ ] Rollback plan rehearsed or approved.
- [ ] Legal/regulatory review complete.
- [ ] Customer/company acceptance signed.
- [ ] Executive release approval signed.

## Residual Risks To Track

| Risk | Severity | Required Disposition |
| --- | --- | --- |
| Formal validation not executed | P0 for regulated production | Execute and approve validation package. |
| Restore drill not complete | P0 for regulated production | Complete restore drill and evidence. |
| Pen test not complete | P0/P1 depending scope | Complete test and remediate or accept findings. |
| SOPs not approved | P0 for regulated production | Approve SOP set and train users/operators. |
| Legal/regulatory language not approved | P0 for customer-facing claims | Approve allowed language and contracts. |
| Executive approval missing | P0 | Obtain signed go/no-go. |
| HSTS preload decision unresolved | P2 | Keep preload disabled until domain policy is approved. |
| PDF/signature export scope unresolved | P2/P3 depending customer need | Decide buyer-specific scope and validation impact. |

## Suggested Timeline

| Phase | Estimated Duration | Dependency |
| --- | --- | --- |
| Governance setup | 1-2 weeks | Named stakeholders. |
| Requirements baseline | 1-2 weeks | Final regulated-use scope. |
| Validation planning | 1-2 weeks | Requirements baseline. |
| Evidence execution | 2-6 weeks | Approved protocols and environment. |
| Security/privacy assurance | 2-4 weeks | Stable release candidate and target environment. |
| Operational qualification | 1-3 weeks | Target infrastructure. |
| SOP/training approval | 1-3 weeks | SOP owners and customer schedule. |
| Legal/regulatory review | 1-3 weeks | Final positioning and contracts. |
| Executive approval | 1 week | Complete release board package. |
| Hypercare | 2-4 weeks | Go-live approval. |

Timeline depends on customer validation model, infrastructure readiness, security findings, SOP approval speed, and contractual requirements.

## Final Roadmap Decision

Decision: ROADMAP READY; REGULATED PRODUCTION NOT APPROVED.

The ecosystem has enough release, validation, security, deployment, commercial, and controlled-production artifacts to start the future regulated production readiness program.

The system must remain positioned as controlled, validation-ready, and audit-ready until the roadmap gates are completed and signed by the responsible organization.

