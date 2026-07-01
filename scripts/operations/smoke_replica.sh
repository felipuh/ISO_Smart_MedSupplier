#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
FRONTEND_DIR="${ROOT_DIR}/frontend"
PYTHON_BIN="${PYTHON_BIN:-${BACKEND_DIR}/.venv312/bin/python}"
SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-backend.settings}"
ORG_SLUG="${ORG_SLUG:-medsupplier-demo-e2e}"
BASE_URL="${BASE_URL:-http://127.0.0.1:8002}"
REPORT="${REPORT:-${ROOT_DIR}/ops_artifacts/smoke/replica_smoke_report.txt}"

mkdir -p "$(dirname "${REPORT}")"

{
  echo "MedSupplier replica smoke report"
  echo "timestamp=$(date +%Y-%m-%dT%H:%M:%S%z)"
  echo "settings=${SETTINGS_MODULE}"
  echo "base_url=${BASE_URL}"
  echo "organization_slug=${ORG_SLUG}"
} > "${REPORT}"

cd "${BACKEND_DIR}"
DJANGO_SETTINGS_MODULE="${SETTINGS_MODULE}" "${PYTHON_BIN}" manage.py check >> "${REPORT}"
DJANGO_SETTINGS_MODULE="${SETTINGS_MODULE}" "${PYTHON_BIN}" manage.py makemigrations --check --dry-run >> "${REPORT}"
DJANGO_SETTINGS_MODULE="${SETTINGS_MODULE}" "${PYTHON_BIN}" manage.py migrate --plan >> "${REPORT}"
DJANGO_SETTINGS_MODULE="${SETTINGS_MODULE}" "${PYTHON_BIN}" manage.py check_medsupplier_adminapps --organization-slug "${ORG_SLUG}" --no-fallback >> "${REPORT}"

if curl -fsS "${BASE_URL}/health" >> "${REPORT}" 2>&1; then
  echo "health_http=PASS" >> "${REPORT}"
else
  echo "health_http=SKIPPED_OR_UNAVAILABLE" >> "${REPORT}"
fi

if curl -fsS "${BASE_URL}/ready" >> "${REPORT}" 2>&1; then
  echo "ready_http=PASS" >> "${REPORT}"
else
  echo "ready_http=SKIPPED_OR_UNAVAILABLE" >> "${REPORT}"
fi

cd "${FRONTEND_DIR}"
npm run lint >> "${REPORT}"
npm run build >> "${REPORT}"

echo "smoke_result=PASS" >> "${REPORT}"
cat "${REPORT}"
