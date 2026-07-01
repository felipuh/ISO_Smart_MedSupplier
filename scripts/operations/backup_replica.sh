#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${ROOT_DIR}/ops_artifacts/backups}"
TIMESTAMP="${TIMESTAMP:-$(date +%Y%m%d_%H%M%S)}"
SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-backend.settings}"
PYTHON_BIN="${PYTHON_BIN:-${BACKEND_DIR}/.venv312/bin/python}"
MANIFEST="${ARTIFACT_ROOT}/medsupplier_replica_${TIMESTAMP}.manifest.txt"

mkdir -p "${ARTIFACT_ROOT}"

echo "MedSupplier replica backup manifest" > "${MANIFEST}"
echo "timestamp=${TIMESTAMP}" >> "${MANIFEST}"
echo "root=${ROOT_DIR}" >> "${MANIFEST}"
echo "settings=${SETTINGS_MODULE}" >> "${MANIFEST}"

cd "${BACKEND_DIR}"

db_engine="$(
  DJANGO_SETTINGS_MODULE="${SETTINGS_MODULE}" "${PYTHON_BIN}" manage.py shell -c \
    "from django.conf import settings; print(settings.DATABASES['default']['ENGINE'])"
)"
db_name="$(
  DJANGO_SETTINGS_MODULE="${SETTINGS_MODULE}" "${PYTHON_BIN}" manage.py shell -c \
    "from django.conf import settings; print(settings.DATABASES['default']['NAME'])"
)"

echo "db_engine=${db_engine}" >> "${MANIFEST}"
echo "db_name=${db_name}" >> "${MANIFEST}"

if [[ "${db_engine}" != *"postgresql"* ]]; then
  echo "PostgreSQL backup refused: ${SETTINGS_MODULE} uses ${db_engine}" >&2
  exit 3
fi

db_host="$(
  DJANGO_SETTINGS_MODULE="${SETTINGS_MODULE}" "${PYTHON_BIN}" manage.py shell -c \
    "from django.conf import settings; print(settings.DATABASES['default'].get('HOST', ''))"
)"
db_port="$(
  DJANGO_SETTINGS_MODULE="${SETTINGS_MODULE}" "${PYTHON_BIN}" manage.py shell -c \
    "from django.conf import settings; print(settings.DATABASES['default'].get('PORT', ''))"
)"
db_user="$(
  DJANGO_SETTINGS_MODULE="${SETTINGS_MODULE}" "${PYTHON_BIN}" manage.py shell -c \
    "from django.conf import settings; print(settings.DATABASES['default'].get('USER', ''))"
)"
db_password="$(
  DJANGO_SETTINGS_MODULE="${SETTINGS_MODULE}" "${PYTHON_BIN}" manage.py shell -c \
    "from django.conf import settings; print(settings.DATABASES['default'].get('PASSWORD', ''))"
)"

db_artifact="${ARTIFACT_ROOT}/medsupplier_postgres_${TIMESTAMP}.dump"
PGPASSWORD="${db_password}" pg_dump \
  --format=custom \
  --no-owner \
  --no-acl \
  --host "${db_host}" \
  --port "${db_port}" \
  --username "${db_user}" \
  --file "${db_artifact}" \
  "${db_name}"

media_artifact="${ARTIFACT_ROOT}/medsupplier_media_${TIMESTAMP}.tar.gz"
if [[ -d "${BACKEND_DIR}/media" ]]; then
  tar --create --gzip --file "${media_artifact}" -C "${BACKEND_DIR}" media
else
  tar --create --gzip --file "${media_artifact}" --files-from /dev/null
fi

sha256sum "${db_artifact}" "${media_artifact}" > "${ARTIFACT_ROOT}/medsupplier_${TIMESTAMP}.sha256"

{
  echo "db_artifact=${db_artifact}"
  echo "db_host=${db_host}"
  echo "db_port=${db_port}"
  echo "db_user=${db_user}"
  echo "media_artifact=${media_artifact}"
  echo "checksum_file=${ARTIFACT_ROOT}/medsupplier_${TIMESTAMP}.sha256"
} >> "${MANIFEST}"

cat "${MANIFEST}"
