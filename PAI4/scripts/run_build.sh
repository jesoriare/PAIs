#!/bin/sh
set -eu

mkdir -p reports/build
docker build -f docker/Dockerfile -t pai4-app:ci . > reports/build/docker-build.log 2>&1
docker image inspect pai4-app:ci > reports/build/image-inspect.json

