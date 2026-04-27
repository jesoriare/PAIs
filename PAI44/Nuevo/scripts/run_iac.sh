#!/bin/sh
set -eu

mkdir -p reports/iac
trivy config --format json -o reports/iac/trivy-iac-report.json docker > reports/iac/trivy.log 2>&1
trivy config --format table docker > reports/iac/trivy-iac.txt 2>> reports/iac/trivy.log
