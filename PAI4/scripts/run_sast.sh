#!/bin/sh
set -eu

mkdir -p reports/sast
semgrep scan \
  --config security/sast/semgrep-rules.yml \
  --output reports/sast/semgrep.txt \
  --json-output=reports/sast/semgrep.json \
  app 2> reports/sast/semgrep.log || true

