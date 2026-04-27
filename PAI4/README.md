# PAI-4 DevSecOps Pipeline

Proyecto DevSecOps completo para la entrega `PAI-4`, preparado como version final del trabajo.

## Resumen

La soluciÃ³n se ha reconstruido desde cero tomando materiales previos solo como referencia de problemas habituales. La decisiÃ³n fue no reutilizar cÃ³digo anterior porque:

- los tests fallaban por errores ajenos al control de seguridad
- el pipeline no estaba preparado para una ejecuciÃ³n limpia y trazable
- habÃ­a configuraciones inseguras como un token de Sonar hardcodeado

La soluciÃ³n final incluye:

- aplicaciÃ³n mÃ­nima en Flask con autenticaciÃ³n, autorizaciÃ³n, formulario validado y cÃ¡lculo de totales en servidor
- una ruta legacy intencionalmente insegura para que SAST y DAST detecten vulnerabilidades reales
- pipeline GitLab CI/CD con las fases obligatorias:
  `sca -> sast -> iac -> test -> build -> deploy -> dast -> vulnerability-management`
- evidencias reales ya generadas en `reports/`

## Documentos principales

- `README.md`: visiÃ³n general del proyecto
- `Manual-Verificacion.md`: guÃ­a paso a paso para comprobar que todo estÃ¡ bien
- `Informe-PAI4.md`: memoria de entrega alineada con el enunciado

## Estructura

```text
PAI44/
â”œâ”€â”€ app/
â”œâ”€â”€ docker/
â”œâ”€â”€ security/
â”œâ”€â”€ tests/
â”œâ”€â”€ reports/
â”œâ”€â”€ scripts/
â”œâ”€â”€ .gitlab-ci.yml
â”œâ”€â”€ README.md
â””â”€â”€ Informe-PAI4.md
```

## AplicaciÃ³n

La app expone:

- `GET /login` y `POST /login`
- `GET /dashboard` protegido por sesiÃ³n
- `GET /admin/audit` restringido a rol `admin`
- `GET/POST /feedback` con validaciÃ³n de entrada y renderizado escapado
- `POST /checkout` con cÃ¡lculo de total exclusivamente en servidor
- `GET /legacy/search` como ruta legacy vulnerable para generar evidencia de scanners
- `GET /health` para despliegue y verificaciÃ³n

## EjecuciÃ³n local

### 1. Tests de seguridad

```powershell
python -m venv .venv
.\\.venv\\Scripts\\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m pytest
```

### 2. Despliegue con Docker Compose

```powershell
$env:PAI4_ADMIN_PASSWORD="cambia-esta-clave"
$env:PAI4_MEMBER_PASSWORD="cambia-esta-clave"
docker compose -f docker/docker-compose.yml up --build
```

La aplicaciÃ³n queda en `http://localhost:5000`.

### 3. ReproducciÃ³n de las fases de seguridad

En GitLab CI se usan directamente los scripts del proyecto:

- `sh scripts/run_sca.sh`
- `sh scripts/run_sast.sh`
- `sh scripts/run_iac.sh`
- `sh scripts/run_tests.sh`
- `sh scripts/run_build.sh`
- `sh scripts/run_deploy.sh`
- `sh scripts/run_dast.sh`
- `sh scripts/run_defectdojo.sh`

En Windows local conviene ejecutar SAST, IaC y DAST con Docker, igual que en CI.

## Variables de CI/CD

Variables recomendadas:

- `DEFECTDOJO_URL`
- `DEFECTDOJO_API_TOKEN`
- `PAI4_ADMIN_PASSWORD` opcional para despliegues deterministas
- `PAI4_MEMBER_PASSWORD` opcional para despliegues deterministas

Si no se definen las credenciales de DefectDojo, la fase `vulnerability-management` no falla: deja constancia de la limitaciÃ³n en `reports/vulnerability-management/`.

## Evidencias generadas

| Fase | Evidencia principal |
| --- | --- |
| SCA | `reports/sca/pip-audit-report.json` |
| SAST | `reports/sast/semgrep.json` |
| IaC | `reports/iac/trivy-iac-report.json` |
| Test | `reports/tests/pytest-report.json` |
| Build | `reports/build/docker-build.log` |
| Deploy | `reports/deploy/healthcheck.json` |
| DAST | `reports/dast/zap-report.json` |
| Vulnerability management | `reports/vulnerability-management/README.md` |

## Hallazgos intencionales

- SCA: `security/sca/requirements-sca.txt` aÃ±ade `urllib3==1.25.8`
- SAST: `app/main.py` usa `Markup(query)` en la ruta legacy
- IaC: `docker/Dockerfile` no define usuario no privilegiado
- DAST: la app no incluye endurecimiento de cabeceras y mantiene la ruta legacy vulnerable

## Endurecimiento recomendado

Para convertir esta demo en una versiÃ³n endurecida:

- actualizar dependencias vulnerables detectadas por `pip-audit`
- eliminar `Markup(query)` y renderizar el input escapado
- aÃ±adir `USER appuser` y `HEALTHCHECK` al Dockerfile
- incorporar protecciÃ³n CSRF, `Content-Security-Policy`, `X-Frame-Options` y `X-Content-Type-Options`

## Informe

La memoria principal estÃ¡ en `Informe-PAI4.md` y referencia las evidencias reales ya presentes en `reports/`.

