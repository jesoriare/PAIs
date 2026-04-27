# PAI 4 - DevSecOps

Seguridad en Sistemas Informaticos y en Internet  
Security Team 9  
Fernando Cobos Garcia  
David Escudero Aldana  
Jesus Oria Arenas  
27/04/2026

## Resumen ejecutivo

Este proyecto implementa una pipeline DevSecOps completa sobre una aplicacion web minima en Flask. El objetivo es demostrar seguridad integrada a lo largo de todo el ciclo de vida del desarrollo con una entrega clara, reproducible y trazable.

La solucion final incluye:

- pipeline GitLab CI/CD con las fases `sca -> sast -> iac -> test -> build -> deploy -> dast -> vulnerability-management`
- aplicacion de prueba con autenticacion, autorizacion, validacion de entrada y logica de negocio en servidor
- integracion de herramientas SCA, SAST, IaC y DAST
- contenedor Docker endurecido con usuario no privilegiado y `HEALTHCHECK`
- separacion entre dependencias de runtime y dependencias de test
- evidencias verificables almacenadas en `reports/`

## Parte I. Informe tecnico

### 1. Alcance y arquitectura

La solucion se implementa integramente en `PAI4/` y se apoya en una aplicacion Flask con almacenamiento SQLite, empaquetado Docker y automatizacion mediante GitLab CI.

| Elemento | Implementacion |
| --- | --- |
| Aplicacion web | Flask |
| Almacenamiento | SQLite |
| Autenticacion | Sesion de Flask |
| Autorizacion | Decoradores por rol |
| Contenedorizacion | Docker |
| Pipeline | GitLab CI/CD |
| SCA | pip-audit |
| SAST | Semgrep |
| IaC | Trivy |
| DAST | OWASP ZAP |
| Gestion de vulnerabilidades | DefectDojo via API |

### 2. Aplicacion de demostracion

| Requisito del proyecto | Implementacion |
| --- | --- |
| Login | `/login` |
| Ruta protegida | `/dashboard` |
| Control de autorizacion | `/admin/audit` |
| Formulario con entrada de usuario | `/feedback` |
| Integridad de negocio | `/checkout` |
| Vulnerabilidad intencional | `/legacy/search` |
| Verificacion de despliegue | `/health` |

Los hallazgos intencionales se introducen para demostrar la pipeline:

- dependencia vulnerable en `security/sca/requirements-sca.txt`
- salida insegura con `Markup(query)` en `app/main.py`
- ausencia de ciertas cabeceras para que ZAP detecte findings reales

### 3. Pipeline CI/CD

La pipeline sigue el orden pedido por el enunciado:

```text
sca -> sast -> iac -> test -> build -> deploy -> dast -> vulnerability-management
```

Cada fase ejecuta un script dedicado y deja artefactos persistentes en `reports/`.

| Fase | Objetivo | Script | Evidencia principal |
| --- | --- | --- | --- |
| SCA | detectar vulnerabilidades en dependencias | `scripts/run_sca.sh` | `reports/sca/pip-audit-report.json` |
| SAST | detectar patrones inseguros en codigo | `scripts/run_sast.sh` | `reports/sast/semgrep.json` |
| IaC | validar el Dockerfile y su endurecimiento | `scripts/run_iac.sh` | `reports/iac/trivy-iac-report.json` |
| Test | verificar controles de seguridad reales | `scripts/run_tests.sh` | `reports/tests/pytest-report.json` |
| Build | construir la imagen Docker | `scripts/run_build.sh` | `reports/build/docker-build.log` |
| Deploy | levantar la aplicacion para validacion | `scripts/run_deploy.sh` | `reports/deploy/healthcheck.json` |
| DAST | escanear la aplicacion en ejecucion | `scripts/run_dast.sh` | `reports/dast/zap-report.json` |
| Vulnerability management | agregar resultados en gestor central | `scripts/run_defectdojo.sh` | `reports/vulnerability-management/README.md` |

### 4. Herramientas integradas

#### 4.1. SCA - pip-audit

`pip-audit` analiza `security/sca/requirements-sca.txt`, donde se anade `urllib3==1.25.8` para asegurar evidencia real.

#### 4.2. SAST - Semgrep

Semgrep usa la regla local `security/sast/semgrep-rules.yml` para detectar el uso inseguro de `Markup(...)` sobre entrada controlada por el usuario.

#### 4.3. IaC - Trivy

Trivy analiza `docker/Dockerfile` para comprobar que la imagen no se ejecuta como `root` y que el endurecimiento basico no se ha perdido.

#### 4.4. DAST - OWASP ZAP

ZAP ejecuta un escaneo completo contra la aplicacion desplegada en contenedor y genera reportes HTML, JSON y XML.

### 5. Pruebas de seguridad

La suite de `tests/security/` verifica controles reales:

- autenticacion obligatoria
- login correcto
- autorizacion por rol
- validacion de entrada
- escape de salida
- no exposicion de material sensible
- integridad de negocio

Evidencia esperada:

- `reports/tests/pytest.log`
- `reports/tests/pytest-report.json`
- `reports/tests/pytest-junit.xml`

Resultado esperado:

- `9 passed`

### 6. Gestion de vulnerabilidades

La integracion con DefectDojo se implementa mediante API REST sobre `/api/v2/reimport-scan/`, consumiendo los reportes de SCA, SAST, IaC y DAST.

La importacion real depende de definir:

- `DEFECTDOJO_URL`
- `DEFECTDOJO_API_TOKEN`

Si no existen, la limitacion queda documentada en `reports/vulnerability-management/`.

## Parte II. Manual de despliegue y uso

### 1. Puesta en marcha rapida

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
$env:PYTHONPATH='.'
.\.venv\Scripts\python -m pytest tests\security
```

Resultado esperado:

- `9 passed`

### 2. Arranque de la aplicacion

```powershell
$env:PAI4_ADMIN_PASSWORD="AdminPassTemporal!123"
$env:PAI4_MEMBER_PASSWORD="MemberPassTemporal!123"
docker compose -f docker\docker-compose.yml up --build
```

La aplicacion queda disponible en:

- `http://localhost:5000/`
- `http://localhost:5000/login`
- `http://localhost:5000/health`

### 3. Evidencias principales

| Categoria | Ruta |
| --- | --- |
| SCA | `reports/sca/` |
| SAST | `reports/sast/` |
| IaC | `reports/iac/` |
| Tests | `reports/tests/` |
| Build | `reports/build/` |
| Deploy | `reports/deploy/` |
| DAST | `reports/dast/` |
| Vulnerability management | `reports/vulnerability-management/` |

## Parte III. Grado de completitud

| Objetivo | Estado | Evidencia |
| --- | --- | --- |
| 1. Definir una pipeline CI/CD | Completo | `.gitlab-ci.yml` |
| 2. Seleccionar al menos tres herramientas de seguridad | Completo | `pip-audit`, `Semgrep`, `Trivy`, `OWASP ZAP` |
| 3. Integrar las herramientas en el ciclo de vida | Completo | scripts y artefactos por fase |
| 4. Desarrollar pruebas para detectar vulnerabilidades | Completo | `tests/security/` y `reports/tests/` |
| 5. Seleccionar e integrar herramienta de gestion | Completo con limitacion documentada | `scripts/run_defectdojo.sh` y `reports/vulnerability-management/` |

## Conclusiones

La entrega satisface los objetivos tecnicos del PAI-4 y presenta una cadena DevSecOps coherente, reproducible y defendible. La solucion prioriza claridad, evidencia y trazabilidad por encima de complejidad innecesaria.
