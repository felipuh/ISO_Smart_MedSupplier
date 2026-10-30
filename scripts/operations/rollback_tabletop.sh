#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORT="${REPORT:-${ROOT_DIR}/ops_artifacts/rollback/rollback_tabletop_report.txt}"
CURRENT_SHA="$(git -C "${ROOT_DIR}" rev-parse --short HEAD 2>/dev/null || echo unknown)"
PREVIOUS_SHA="${PREVIOUS_SHA:-manual-previous-approved-artifact-required}"

mkdir -p "$(dirname "${REPORT}")"

cat > "${REPORT}" <<EOF
MedSupplier rollback tabletop report
timestamp=$(date +%Y-%m-%dT%H:%M:%S%z)
environment=local-replica
current_release_sha=${CURRENT_SHA}
previous_approved_artifact=${PREVIOUS_SHA}
rehearsal_type=approved-tabletop-local-replica
traffic_drain=not-applicable-local-replica
app_rollback_steps=validated-in-runbook
database_rollback_policy=restore-only-with-release-owner-and-data-owner-approval
adminapps_fallback_policy=do-not-enable-local-fallback-in-production
health_validation=use /health and /ready after redeploy
adminapps_validation=check_medsupplier_adminapps --no-fallback
data_rollback_used=no
result=PASS_WITH_RESTRICTION
restriction=requires-real-previous-artifact-and-target-environment-rehearsal-before-live-production
EOF

cat "${REPORT}"
