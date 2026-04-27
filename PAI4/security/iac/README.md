# IaC scope

`Trivy` scans `docker/Dockerfile`.

The Dockerfile intentionally omits a non-root `USER` directive so the IaC stage produces a real misconfiguration finding in `reports/iac/`.
