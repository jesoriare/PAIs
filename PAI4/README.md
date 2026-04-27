# PAI-4 DevSecOps Pipeline

Proyecto DevSecOps completo para la entrega `PAI-4`, preparado como version final dentro de `PAI4/`.

## Resumen

La solucion final consolida lo mejor de las versiones previas y elimina restos que podian confundir la entrega.

Incluye:

- aplicacion minima en Flask con autenticacion, autorizacion, validacion de entrada y calculo de negocio en servidor
- una ruta legacy vulnerable para generar evidencia real en SAST y DAST
- contenedor endurecido con usuario no privilegiado y `HEALTHCHECK`
- separacion entre dependencias de ejecucion y de test
- pipeline GitLab CI/CD con las fases `sca -> sast -> iac -> test -> build -> deploy -> dast -> vulnerability-management`
- evidencias reales ya generadas en `reports/`

## Estructura

```text
PAI4/
|-- app/
|-- docker/
|-- reports/
|-- scripts/
|-- security/
|-- tests/
|-- .gitlab-ci.yml
|-- Informe-PAI4.md
|-- Manual-Verificacion.md
|-- README.md
|-- requirements.txt
`-- requirements-dev.txt
```

## Aplicacion

La app expone:

- `GET /login` y `POST /login`
- `GET /dashboard` protegido por sesion
- `GET /admin/audit` restringido a rol `admin`
- `GET/POST /feedback` con validacion de entrada y renderizado escapado
- `POST /checkout` con calculo de total exclusivamente en servidor
- `GET /legacy/search` como ruta legacy vulnerable para evidencia de scanners
- `GET /health` para despliegue y verificacion

## Ejecucion local

### 1. Tests de seguridad

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m pytest
```

### 2. Despliegue con Docker Compose

```powershell
$env:PAI4_ADMIN_PASSWORD="cambia-esta-clave"
$env:PAI4_MEMBER_PASSWORD="cambia-esta-clave"
docker compose -f docker/docker-compose.yml up --build
```

La aplicacion queda disponible en `http://localhost:5000`.

## Pipeline

La pipeline usa directamente:

- `scripts/run_sca.sh`
- `scripts/run_sast.sh`
- `scripts/run_iac.sh`
- `scripts/run_tests.sh`
- `scripts/run_build.sh`
- `scripts/run_deploy.sh`
- `scripts/run_dast.sh`
- `scripts/run_defectdojo.sh`

## Hallazgos intencionales

- SCA: `security/sca/requirements-sca.txt` anade `urllib3==1.25.8`
- SAST: `app/main.py` usa `Markup(query)` en la ruta legacy
- DAST: la app mantiene una superficie minima suficiente para generar findings reales

## Entrega recomendada

Para la entrega final, empaquetad unicamente el contenido de `PAI4/` con el nombre solicitado por el enunciado, por ejemplo `PAI4-ST9.zip`.
Si cambiais codigo, pipeline o Dockerfile, regenerad los artefactos de `reports/` antes de comprimir.
