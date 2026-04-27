#!/bin/sh
set -eu

REPORT_DIR="reports/vulnerability-management"
ATTEMPTS_FILE="$REPORT_DIR/attempts.tsv"
SUMMARY_FILE="$REPORT_DIR/README.md"

mkdir -p "$REPORT_DIR"
printf 'scan_type\treport\thttp_code\n' > "$ATTEMPTS_FILE"

if [ -z "${DEFECTDOJO_URL:-}" ] || [ -z "${DEFECTDOJO_API_TOKEN:-}" ]; then
  cat > "$SUMMARY_FILE" <<'EOF'
# DefectDojo integration attempt

The repository includes a working `curl`-based integration against DefectDojo's `/api/v2/reimport-scan/` endpoint.

This execution did not perform a live import because `DEFECTDOJO_URL` and/or `DEFECTDOJO_API_TOKEN` were not provided as CI variables.

Once those variables are configured, rerun the `vulnerability-management` stage to upload:
- `reports/sca/pip-audit-report.json`
- `reports/sast/semgrep.json`
- `reports/iac/trivy-iac-report.json`
- `reports/dast/zap-report.json`
EOF
  exit 0
fi

submit_report() {
  scan_type="$1"
  report_path="$2"
  test_title="$3"
  response_file="$4"

  http_code="$(curl -sS -o "$response_file" -w '%{http_code}' \
    -X POST "${DEFECTDOJO_URL%/}/api/v2/reimport-scan/" \
    -H "Authorization: Token ${DEFECTDOJO_API_TOKEN}" \
    -F "scan_type=${scan_type}" \
    -F "minimum_severity=Info" \
    -F "active=true" \
    -F "verified=false" \
    -F "auto_create_context=true" \
    -F "product_type_name=PAI" \
    -F "product_name=PAI4 DevSecOps Pipeline" \
    -F "engagement_name=PAI44 Evidence" \
    -F "test_title=${test_title}" \
    -F "file=@${report_path}")"

  printf '%s\t%s\t%s\n' "$scan_type" "$report_path" "$http_code" >> "$ATTEMPTS_FILE"
}

submit_report "Pip-Audit Scan" "reports/sca/pip-audit-report.json" "SCA" "$REPORT_DIR/pip-audit-response.json"
submit_report "Semgrep JSON Report" "reports/sast/semgrep.json" "SAST" "$REPORT_DIR/semgrep-response.json"
submit_report "Trivy Scan" "reports/iac/trivy-iac-report.json" "IaC" "$REPORT_DIR/trivy-response.json"
submit_report "ZAP Scan" "reports/dast/zap-report.json" "DAST" "$REPORT_DIR/zap-response.json"

cat > "$SUMMARY_FILE" <<'EOF'
# DefectDojo integration attempt

The stage executed live API requests against DefectDojo's `/api/v2/reimport-scan/` endpoint.

Review `attempts.tsv` and the response JSON files in this directory to confirm which imports were accepted by the target instance.
EOF
