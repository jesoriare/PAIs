#!/bin/sh

set -eu

mkdir -p reports/tests
pytest -q --junitxml=reports/tests/pytest-junit.xml 2>&1 | tee reports/tests/pytest.log
