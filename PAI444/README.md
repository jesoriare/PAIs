# PAI-4 DevSecOps Pipeline

Proyecto DevSecOps completo para la entrega `PAI-4`, implementado por completo dentro de `Nuevo/`.

## Resumen

La solución se ha reconstruido desde cero tomando `Fran/` solo como referencia de problemas previos. La decisión fue no reutilizar su código porque:

- los tests fallaban por errores ajenos al control de seguridad
- el pipeline no estaba preparado para una ejecución limpia y trazable
- había configuraciones inseguras como un token de Sonar hardcodeado

La solución final incluye:

- aplicación mínima en Flask con autenticación, autorización, formulario validado y cálculo de totales en servidor
- una ruta legacy intencionalmente insegura para que SAST y DAST detecten vulnerabilidades reales
- contenedor endurecido con usuario no privilegiado y `HEALTHCHECK`
- separación entre dependencias de ejecución y de test
- pipeline GitLab CI/CD con las fases obligatorias:
  `sca -> sast -> iac -> test -> build -> deploy -> dast -> vulnerability-management`
- evidencias reales ya generadas en `reports/`

## Documentos principales

- `README.md`: visión general del proyecto
- `Manual-Verificacion.md`: guía paso a paso para comprobar que todo está bien
- `Informe-PAI4.md`: memoria de entrega alineada con el enunciado

## Estructura

```text
Nuevo/
├── app/
├── docker/
├── security/
├── tests/
├── reports/
├── scripts/
├── .gitlab-ci.yml
├── README.md
└── Informe-PAI4.md
```

## Aplicación

La app expone:

- `GET /login` y `POST /login`
- `GET /dashboard` protegido por sesión
- `GET /admin/audit` restringido a rol `admin`
- `GET/POST /feedback` con validación de entrada y renderizado escapado
- `POST /checkout` con cálculo de total exclusivamente en servidor
- `GET /legacy/search` como ruta legacy vulnerable para generar evidencia de scanners
- `GET /health` para despliegue y verificación

## Ejecución local

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

La aplicación queda en `http://localhost:5000`.

### 3. Reproducción de las fases de seguridad

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

Si no se definen las credenciales de DefectDojo, la fase `vulnerability-management` no falla: deja constancia de la limitación en `reports/vulnerability-management/`.

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

- SCA: `security/sca/requirements-sca.txt` añade `urllib3==1.25.8`
- SAST: `app/main.py` usa `Markup(query)` en la ruta legacy
- DAST: la app no incluye endurecimiento de cabeceras y mantiene la ruta legacy vulnerable

## Endurecimiento recomendado

Para convertir esta demo en una versión endurecida:

- actualizar dependencias vulnerables detectadas por `pip-audit`
- eliminar `Markup(query)` y renderizar el input escapado
- incorporar protección CSRF, `Content-Security-Policy`, `X-Frame-Options` y `X-Content-Type-Options`

## Entrega recomendada

Para la entrega final, empaquetad únicamente el contenido de `Nuevo/` con el nombre solicitado por el enunciado, por ejemplo `PAI4-ST9.zip`.
Si tocáis código o documentación antes de comprimir, regenerad los artefactos de `reports/` para que queden alineados con la versión final.

## Informe

La memoria principal está en `Informe-PAI4.md` y referencia las evidencias reales ya presentes en `reports/`.
