#!/bin/sh
set -eu

mkdir -p reports/sca
pip-audit -r security/sca/requirements-sca.txt --format json > reports/sca/pip-audit-report.json 2> reports/sca/pip-audit.log || true
pip-audit -r security/sca/requirements-sca.txt > reports/sca/pip-audit.txt 2>> reports/sca/pip-audit.log || true

