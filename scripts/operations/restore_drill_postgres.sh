#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
PYTHON_BIN="${PYTHON_BIN:-${BACKEND_DIR}/.venv312/bin/python}"
SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-backend.settings}"
SOURCE_DUMP="${1:-}"
TIMESTAMP="${TIMESTAMP:-$(date +%Y%m%d_%H%M%S)}"
RESTORE_DB_NAME="${RESTORE_DB_NAME:-medsupplier_restore_drill_${TIMESTAMP}}"
RESTORE_DB_PRECREATED="${RESTORE_DB_PRECREATED:-false}"
REPORT="${REPORT:-${ROOT_DIR}/ops_artifacts/restore/restore_drill_postgres_${TIMESTAMP}.txt}"

if [[ -z "${SOURCE_DUMP}" ]]; then
  echo "usage: $0 <postgres-custom-dump-artifact>" >&2
  exit 2
fi

mkdir -p "$(dirname "${REPORT}")"

cd "${BACKEND_DIR}"

read_db_setting() {
  local key="$1"
  DJANGO_SETTINGS_MODULE="${SETTINGS_MODULE}" "${PYTHON_BIN}" manage.py shell -c \
    "from django.conf import settings; print(settings.DATABASES['default'].get('${key}', ''))"
}

db_engine="$(read_db_setting ENGINE)"
db_host="$(read_db_setting HOST)"
db_port="$(read_db_setting PORT)"
db_user="$(read_db_setting USER)"
db_password="$(read_db_setting PASSWORD)"

if [[ "${db_engine}" != *"postgresql"* ]]; then
  echo "PostgreSQL restore drill refused: ${SETTINGS_MODULE} uses ${db_engine}" >&2
  exit 3
fi

cat > "${REPORT}" <<EOF
MedSupplier PostgreSQL restore drill report
timestamp=$(date +%Y-%m-%dT%H:%M:%S%z)
settings=${SETTINGS_MODULE}
source_dump=${SOURCE_DUMP}
restore_db_name=${RESTORE_DB_NAME}
db_host=${db_host}
db_port=${db_port}
db_user=${db_user}
EOF

if [[ "${RESTORE_DB_PRECREATED}" != "true" ]]; then
  if ! PGPASSWORD="${db_password}" createdb \
    --host "${db_host}" \
    --port "${db_port}" \
    --username "${db_user}" \
    "${RESTORE_DB_NAME}" 2>> "${REPORT}"; then
    {
      echo "restore_result=BLOCKED"
      echo "blocker=database role cannot create restore drill database"
      echo "required_action=create an empty PostgreSQL database owned by ${db_user}, then rerun with RESTORE_DB_NAME=<name> RESTORE_DB_PRECREATED=true"
    } >> "${REPORT}"
    cat "${REPORT}"
    exit 4
  fi
else
  echo "restore_db_creation=skipped_precreated" >> "${REPORT}"
fi

PGPASSWORD="${db_password}" pg_restore \
  --host "${db_host}" \
  --port "${db_port}" \
  --username "${db_user}" \
  --no-owner \
  --no-acl \
  --dbname "${RESTORE_DB_NAME}" \
  "${SOURCE_DUMP}"

RESTORE_DB_NAME="${RESTORE_DB_NAME}" DJANGO_SETTINGS_MODULE=backend.settings_restore_drill_postgres \
  "${PYTHON_BIN}" manage.py shell -c \
  "from django.db import connection; cursor=connection.cursor(); cursor.execute('select 1'); print('database_probe=ok')" \
  >> "${REPORT}"

RESTORE_DB_NAME="${RESTORE_DB_NAME}" DJANGO_SETTINGS_MODULE=backend.settings_restore_drill_postgres \
  "${PYTHON_BIN}" manage.py check >> "${REPORT}"

RESTORE_DB_NAME="${RESTORE_DB_NAME}" DJANGO_SETTINGS_MODULE=backend.settings_restore_drill_postgres \
  "${PYTHON_BIN}" manage.py migrate --plan >> "${REPORT}"

echo "restore_result=PASS" >> "${REPORT}"
cat "${REPORT}"
