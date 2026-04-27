#!/bin/sh
set -eu

mkdir -p reports/deploy

ADMIN_PASSWORD="${PAI4_ADMIN_PASSWORD:-admin-$(date +%s)}"
MEMBER_PASSWORD="${PAI4_MEMBER_PASSWORD:-member-$(date +%s)}"

docker network create pai4-net > reports/deploy/network.log 2>&1 || true
docker rm -f pai4-app > /dev/null 2>&1 || true
docker run -d \
  --name pai4-app \
  --network pai4-net \
  -p 5000:5000 \
  -e PAI4_DB_PATH=/opt/pai4/data/app.db \
  -e PAI4_ADMIN_USERNAME="${PAI4_ADMIN_USERNAME:-admin}" \
  -e PAI4_MEMBER_USERNAME="${PAI4_MEMBER_USERNAME:-member}" \
  -e PAI4_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  -e PAI4_MEMBER_PASSWORD="$MEMBER_PASSWORD" \
  pai4-app:ci > reports/deploy/container-id.txt

sleep 10
docker run --rm --network pai4-net curlimages/curl:8.11.1 curl -fsS http://pai4-app:5000/health > reports/deploy/healthcheck.json
docker ps --filter name=pai4-app --format '{{.ID}} {{.Image}} {{.Status}} {{.Ports}}' > reports/deploy/docker-ps.txt
docker logs pai4-app > reports/deploy/app.log 2>&1
