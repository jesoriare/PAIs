# Grado de completitud

## Objetivo 1. Definir pipeline CI/CD

- Cumplido: se incluye `.gitlab-ci.yml` con etapas `SCA`, `SAST`, `IaC`, `Test`, `Build`, `DAST` y `Vulnerability-Management`.

## Objetivo 2. Seleccionar al menos tres herramientas

- Cumplido: `pip-audit`, `Bandit`, `Trivy` y `OWASP ZAP`.

## Objetivo 3. Integrar herramientas en el ciclo de vida

- Cumplido: todas las herramientas quedan integradas en el pipeline.

## Objetivo 4. Desarrollar tests

- Cumplido: se incluyen tests funcionales y de seguridad con `pytest`.

## Objetivo 5. Seleccionar herramienta de gestion de vulnerabilidades

- Cumplido parcialmente: se selecciona `DefectDojo` y se incluye script de importacion, quedando su uso final condicionado a la configuracion de credenciales.
