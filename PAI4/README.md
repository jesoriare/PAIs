# PAI4 - DevSecOps Supply Chain

Proyecto de prueba para el `PAI 4`, centrado en montar un pipeline `DevSecOps`
para una aplicacion web pequena.

## Stack

- `Flask` para la aplicacion web
- `pytest` para tests automatizados
- `pip-audit` para `SCA`
- `Bandit` para `SAST`
- `Trivy` para `Security IaC`
- `OWASP ZAP` para `DAST`
- `DefectDojo` como herramienta de gestion de vulnerabilidades propuesta

## Estructura

- `app.py`: punto de entrada de la aplicacion
- `src/pai4_app/`: logica principal de la app
- `tests/`: tests funcionales y de seguridad
- `.gitlab-ci.yml`: pipeline `CI/CD` y etapas `DevSecOps`
- `.semgrep.yml`: reglas locales de analisis estatico
- `Dockerfile`: construccion de imagen
- `deployment/`: artefactos de despliegue simples
- `scripts/`: scripts auxiliares de ejecucion e integracion
- `docs/`: material de apoyo para informe y manual

## Ejecucion local

```powershell
cd PAI4
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python app.py
```

La app quedara disponible en `http://127.0.0.1:5000`.

## Tests

```powershell
pytest
```

## Herramientas de seguridad local

### SCA

```powershell
pip-audit -r requirements.txt -f json -o reports/sca/pip-audit-report.json
```

### SAST

```powershell
bandit -r src tests -f json -o reports/sast/bandit-report.json
```

### IaC

```powershell
trivy config --format json -o reports/iac/trivy-config-report.json .
```

### DAST

Con la app levantada:

```powershell
docker run --rm -t owasp/zap2docker-stable zap-baseline.py -t http://host.docker.internal:5000 -J /zap/wrk/zap-report.json
```
