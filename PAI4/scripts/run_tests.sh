#!/bin/sh
set -eu

mkdir -p reports/tests
export PYTHONPATH="${PYTHONPATH:-.}:."
pytest \
  --junitxml=reports/tests/pytest-junit.xml \
  --json-report \
  --json-report-file=reports/tests/pytest-report.json \
  tests/security > reports/tests/pytest.log 2>&1

