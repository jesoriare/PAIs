#!/bin/sh
set -eu

mkdir -p reports/dast

ADMIN_PASSWORD="${PAI4_ADMIN_PASSWORD:-admin-$(date +%s)}"
MEMBER_PASSWORD="${PAI4_MEMBER_PASSWORD:-member-$(date +%s)}"

docker network create pai4-zap-net > reports/dast/network.log 2>&1 || true
docker rm -f pai4-app-dast > /dev/null 2>&1 || true
docker run -d \
  --name pai4-app-dast \
  --network pai4-zap-net \
  -e PAI4_DB_PATH=/opt/pai4/data/app.db \
  -e PAI4_ADMIN_USERNAME="${PAI4_ADMIN_USERNAME:-admin}" \
  -e PAI4_MEMBER_USERNAME="${PAI4_MEMBER_USERNAME:-member}" \
  -e PAI4_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  -e PAI4_MEMBER_PASSWORD="$MEMBER_PASSWORD" \
  pai4-app:ci > reports/dast/container-id.txt

sleep 10
docker run --rm --network pai4-zap-net curlimages/curl:8.11.1 curl -fsS http://pai4-app-dast:5000/ > reports/dast/pre-scan-home.html
docker run --rm \
  --network pai4-zap-net \
  -v "$PWD/reports/dast:/zap/wrk/:rw" \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-full-scan.py \
  -t http://pai4-app-dast:5000 \
  -m 1 \
  -T 5 \
  -I \
  -J zap-report.json \
  -r zap-report.html \
  -x zap-report.xml > reports/dast/zap.log 2>&1 || true

docker logs pai4-app-dast > reports/dast/app.log 2>&1

