# SCA scope

`pip-audit` scans `security/sca/requirements-sca.txt`.

That manifest extends the runtime dependencies and intentionally adds `urllib3==1.25.8` so the SCA stage produces verifiable evidence in `reports/sca/` without weakening the app execution path.
