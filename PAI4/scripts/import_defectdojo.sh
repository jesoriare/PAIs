#!/bin/sh

set -eu

if [ -z "${DEFECTDOJO_URL:-}" ] || [ -z "${DEFECTDOJO_TOKEN:-}" ]; then
  echo "Faltan DEFECTDOJO_URL o DEFECTDOJO_TOKEN"
  exit 1
fi

curl -X POST "${DEFECTDOJO_URL}/import-scan/" \
  -H "Authorization: Token ${DEFECTDOJO_TOKEN}" \
  -F "file=@reports/sca/pip-audit-report.json" \
  -F "scan_type=Python Audit Scan" \
  -F "engagement_name=PAI4-SCA"
