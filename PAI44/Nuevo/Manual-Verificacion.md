# Manual de Verificación Completa

## Objetivo

Este documento explica, paso a paso y sin asumir contexto previo, cómo comprobar que el proyecto `PAI-4` de la carpeta `Nuevo/` está correcto, que los controles de seguridad funcionan, que la aplicación arranca, que los artefactos se generan y que las evidencias coinciden con lo que exige el enunciado.

La idea es que puedas usar este manual para:

- validar la entrega antes de comprimirla
- repetir las pruebas si cambias algo
- demostrar al profesor que la solución es reproducible
- saber qué resultado esperar en cada fase

## Qué se va a comprobar

La validación completa cubre estas áreas:

| Área | Qué se comprueba |
| --- | --- |
| Estructura | Que `Nuevo/` contiene todos los ficheros y carpetas exigidos |
| Aplicación | Que la app Flask arranca y responde |
| Tests | Que los tests de seguridad pasan |
| SCA | Que `pip-audit` detecta vulnerabilidades reales |
| SAST | Que Semgrep detecta el patrón inseguro intencional |
| IaC | Que Trivy detecta malas prácticas en el Dockerfile |
| Build | Que la imagen Docker se construye correctamente |
| Deploy | Que el contenedor queda levantado y el healthcheck responde |
| DAST | Que ZAP encuentra hallazgos reales contra la app en ejecución |
| Gestión de vulnerabilidades | Que existe el intento de integración con DefectDojo y queda trazabilidad |

## Antes de empezar

### Ruta de trabajo

Abre PowerShell y sitúate aquí:

```powershell
cd C:\Users\david\PAI\PAIs\PAI4\Nuevo
```

Todas las órdenes de este documento asumen esa ruta.

### Requisitos previos

Debes tener disponible:

- Python 3.11 o superior
- Docker Desktop arrancado
- acceso a Internet para descargar imágenes Docker y paquetes Python

### Comprobaciones iniciales

Ejecuta:

```powershell
python --version
docker --version
docker info
```

Qué debes esperar:

- `python --version` devuelve una versión válida
- `docker --version` devuelve versión instalada
- `docker info` no da error y confirma que Docker Desktop está levantado

Si `docker info` falla:

1. abre Docker Desktop
2. espera a que indique que está listo
3. vuelve a lanzar `docker info`

## 1. Comprobar la estructura del proyecto

### Qué hacer

Ejecuta:

```powershell
Get-ChildItem -Force
```

### Qué debe existir en la raíz de `Nuevo/`

Debes ver como mínimo:

- `app`
- `docker`
- `reports`
- `scripts`
- `security`
- `tests`
- `.gitlab-ci.yml`
- `README.md`
- `Informe-PAI4.md`
- `Manual-Verificacion.md`
- `requirements.txt`
- `pytest.ini`

### Verificación adicional

Puedes listar todos los archivos relevantes:

```powershell
Get-ChildItem app,docker,scripts,security,tests -Recurse -File
```

Debes ver, entre otros:

- `app\main.py`
- `app\db.py`
- `docker\Dockerfile`
- `docker\docker-compose.yml`
- `scripts\run_sca.sh`
- `scripts\run_sast.sh`
- `scripts\run_iac.sh`
- `scripts\run_tests.sh`
- `scripts\run_build.sh`
- `scripts\run_deploy.sh`
- `scripts\run_dast.sh`
- `scripts\run_defectdojo.sh`
- `security\sast\semgrep-rules.yml`
- `security\sca\requirements-sca.txt`
- `tests\security\test_authentication.py`

Si falta alguno de esos archivos, no sigas con la verificación: primero habría que corregir la estructura.

## 2. Preparar entorno Python para tests

### Crear entorno virtual

Ejecuta:

```powershell
python -m venv .venv
```

### Instalar dependencias

Ejecuta:

```powershell
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

### Qué debes esperar

- instalación correcta sin errores
- paquetes principales instalados:
  `Flask`, `gunicorn`, `pytest`, `pytest-json-report`

## 3. Ejecutar y validar los tests de seguridad

### Ejecutar tests

Ejecuta:

```powershell
$env:PYTHONPATH='.'
.\.venv\Scripts\python -m pytest --junitxml=reports\tests\pytest-junit.xml --json-report --json-report-file=reports\tests\pytest-report.json tests\security
```

### Qué debes esperar

El resultado correcto es:

```text
9 passed
```

### Qué controles están cubiertos

| Test | Qué valida |
| --- | --- |
| `test_dashboard_requires_login` | que no se entra al dashboard sin login |
| `test_successful_login_sets_session_and_redirects_to_dashboard` | que el login correcto crea sesión |
| `test_member_cannot_access_admin_route` | que un usuario normal no entra a la ruta admin |
| `test_admin_can_access_admin_route` | que un admin sí puede entrar |
| `test_feedback_rejects_overlong_input` | que la entrada excesiva se bloquea |
| `test_checkout_rejects_invalid_quantities` | que cantidades inválidas se rechazan |
| `test_feedback_output_is_escaped` | que el contenido del usuario se escapa y no se ejecuta |
| `test_profile_omits_password_material` | que no se expone material sensible |
| `test_checkout_total_is_calculated_server_side` | que el total lo calcula el servidor |

### Artefactos a revisar

Después de ejecutar los tests deben existir:

- `reports\tests\pytest.log`
- `reports\tests\pytest-junit.xml`
- `reports\tests\pytest-report.json`

### Verificación rápida de artefactos

```powershell
Get-ChildItem reports\tests
Get-Content reports\tests\pytest.log
```

Debes ver al final del log una línea equivalente a:

```text
9 passed
```

## 4. Validar la aplicación manualmente

Esta parte sirve para comprobar la aplicación sin scanners, como si fueras un usuario.

### Levantar la app con Docker Compose

Ejecuta:

```powershell
$env:PAI4_ADMIN_PASSWORD="AdminPassTemporal!123"
$env:PAI4_MEMBER_PASSWORD="MemberPassTemporal!123"
docker compose -f docker\docker-compose.yml up --build
```

Déjalo arrancado.

### Qué debes esperar en consola

Mensajes parecidos a:

- instalación de dependencias
- `Bootstrapped users into /opt/pai4/data/app.db`
- `Starting gunicorn`
- `Listening at: http://0.0.0.0:5000`

### Qué comprobar en navegador

Abre:

- `http://localhost:5000/`
- `http://localhost:5000/health`
- `http://localhost:5000/login`

### Resultado esperado

| URL | Resultado esperado |
| --- | --- |
| `/` | home visible |
| `/health` | `{"status":"ok"}` |
| `/login` | formulario de login |

### Qué comprobar manualmente con lógica de seguridad

#### Comprobar autenticación

1. abre `http://localhost:5000/dashboard`
2. sin haber iniciado sesión, debe redirigir al login

#### Comprobar autorización

Este flujo está mejor cubierto por tests, pero puedes validarlo así:

1. inicia sesión con un usuario normal si adaptas el formulario a tus credenciales creadas por entorno
2. intenta acceder a `/admin/audit`
3. debe devolver `403`

#### Comprobar validación

1. entra a `/feedback` tras login
2. envía un mensaje normal
3. debe guardarse
4. si modificas manualmente el formulario para mandar más de 200 caracteres, debe rechazarse

#### Comprobar integridad de negocio

La comprobación fuerte la hacen los tests, pero la lógica del endpoint `/checkout` está pensada para ignorar el total enviado por el cliente y calcular el suyo propio.

### Parar la aplicación

En la misma terminal:

```powershell
Ctrl + C
docker compose -f docker\docker-compose.yml down
```

## 5. Ejecutar y validar SCA

### Qué se está comprobando

`pip-audit` escanea `security\sca\requirements-sca.txt`.

Ese fichero añade intencionalmente:

```text
urllib3==1.25.8
```

para que la fase SCA detecte vulnerabilidades reales.

### Preparar entorno aislado para SCA

Ejecuta:

```powershell
python -m venv .audit-venv
.\.audit-venv\Scripts\python -m pip install --upgrade pip pip-audit
```

### Ejecutar SCA

Ejecuta:

```powershell
.\.audit-venv\Scripts\pip-audit -r security\sca\requirements-sca.txt --format json 1> reports\sca\pip-audit-report.json 2> reports\sca\pip-audit.log
.\.audit-venv\Scripts\pip-audit -r security\sca\requirements-sca.txt 1> reports\sca\pip-audit.txt 2>> reports\sca\pip-audit.log
```

### Qué debes esperar

No esperes un “todo limpio”. Aquí lo correcto es que encuentre vulnerabilidades.

Como mínimo debe haber findings sobre `urllib3==1.25.8`.

### Artefactos esperados

- `reports\sca\pip-audit-report.json`
- `reports\sca\pip-audit.txt`
- `reports\sca\pip-audit.log`

### Verificación rápida

```powershell
Get-Content reports\sca\pip-audit.txt
```

Debes ver referencias a `urllib3 1.25.8` y sus fixes recomendados.

## 6. Ejecutar y validar SAST

### Qué se está comprobando

Semgrep usa la regla local:

- `security\sast\semgrep-rules.yml`

La regla detecta:

- `Markup(query)` con entrada controlada por el usuario

Eso apunta a la vulnerabilidad intencional de:

- `app\main.py`
- ruta `/legacy/search`

### Ejecutar SAST

Desde PowerShell:

```powershell
$cwd = (Get-Location).Path
docker run --rm -v "${cwd}:/src" -w /src semgrep/semgrep:latest sh scripts/run_sast.sh
```

### Qué debes esperar

No debe salir “0 findings”. Lo correcto es que aparezca 1 hallazgo.

### Artefactos esperados

- `reports\sast\semgrep.json`
- `reports\sast\semgrep.txt`
- `reports\sast\semgrep.log`

### Verificación rápida

```powershell
Get-Content reports\sast\semgrep.txt
```

Debes ver un finding sobre:

- `security.sast.flask-legacy-markup-user-input`
- `app/main.py`

## 7. Ejecutar y validar IaC

### Qué se está comprobando

Trivy analiza:

- `docker\Dockerfile`

El Dockerfile contiene a propósito una mala práctica:

- no define usuario no root con `USER`

También puede detectar:

- falta de `HEALTHCHECK`

### Ejecutar IaC

```powershell
$cwd = (Get-Location).Path
docker run --rm --entrypoint sh -v "${cwd}:/work" -w /work aquasec/trivy:latest scripts/run_iac.sh
```

### Artefactos esperados

- `reports\iac\trivy-iac-report.json`
- `reports\iac\trivy-iac.txt`
- `reports\iac\trivy.log`

### Verificación rápida

```powershell
Get-Content reports\iac\trivy-iac.txt
```

Debes ver como mínimo:

- `DS-0002` por falta de usuario no root

Puede aparecer también:

- `DS-0026` por falta de `HEALTHCHECK`

## 8. Ejecutar y validar Build

### Qué se está comprobando

Que la imagen Docker de la aplicación se construye correctamente.

### Ejecutar Build

```powershell
docker build -f docker/Dockerfile -t pai4-app:ci . 1> reports\build\docker-build.log 2>&1
docker image inspect pai4-app:ci | Out-File -FilePath reports\build\image-inspect.json -Encoding utf8
```

### Qué debes esperar

- build sin errores
- imagen `pai4-app:ci` creada

### Verificación rápida

```powershell
docker images | Select-String pai4-app
Get-Content reports\build\docker-build.log
```

## 9. Ejecutar y validar Deploy

### Qué se está comprobando

Que la imagen recién construida arranca como contenedor y responde a `/health`.

### Ejecutar Deploy

```powershell
docker network create pai4-net 1> reports\deploy\network.log 2>&1
```

Luego:

```powershell
$adminPass = 'admin-' + [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$memberPass = 'member-' + [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
docker rm -f pai4-app *> $null
docker run -d --name pai4-app --network pai4-net -p 5000:5000 -e PAI4_DB_PATH=/opt/pai4/data/app.db -e PAI4_ADMIN_USERNAME=admin -e PAI4_MEMBER_USERNAME=member -e PAI4_ADMIN_PASSWORD=$adminPass -e PAI4_MEMBER_PASSWORD=$memberPass pai4-app:ci | Out-File -FilePath reports\deploy\container-id.txt -Encoding ascii
Start-Sleep -Seconds 10
docker run --rm --network pai4-net curlimages/curl:8.11.1 curl -fsS http://pai4-app:5000/health | Out-File -FilePath reports\deploy\healthcheck.json -Encoding ascii
docker ps --filter name=pai4-app --format '{{.ID}} {{.Image}} {{.Status}} {{.Ports}}' | Out-File -FilePath reports\deploy\docker-ps.txt -Encoding ascii
docker logs pai4-app 1> reports\deploy\app.log 2>&1
```

### Resultado esperado

| Comprobación | Resultado esperado |
| --- | --- |
| Contenedor | `Up` |
| Puerto | `5000` expuesto |
| Healthcheck | `{"status":"ok"}` |

### Archivos esperados

- `reports\deploy\container-id.txt`
- `reports\deploy\healthcheck.json`
- `reports\deploy\docker-ps.txt`
- `reports\deploy\app.log`

## 10. Ejecutar y validar DAST

### Qué se está comprobando

Que ZAP escanea la aplicación en ejecución y detecta hallazgos reales.

### Ejecutar DAST

```powershell
docker network create pai4-zap-net 1> reports\dast\network.log 2>&1
```

Luego:

```powershell
$adminPass = 'admin-' + [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$memberPass = 'member-' + [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
docker rm -f pai4-app-dast *> $null
docker run -d --name pai4-app-dast --network pai4-zap-net -e PAI4_DB_PATH=/opt/pai4/data/app.db -e PAI4_ADMIN_USERNAME=admin -e PAI4_MEMBER_USERNAME=member -e PAI4_ADMIN_PASSWORD=$adminPass -e PAI4_MEMBER_PASSWORD=$memberPass pai4-app:ci | Out-File -FilePath reports\dast\container-id.txt -Encoding ascii
Start-Sleep -Seconds 10
docker run --rm --network pai4-zap-net curlimages/curl:8.11.1 curl -fsS http://pai4-app-dast:5000/ | Out-File -FilePath reports\dast\pre-scan-home.html -Encoding utf8
docker run --rm --network pai4-zap-net -v "${PWD}\reports\dast:/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable zap-full-scan.py -t http://pai4-app-dast:5000 -m 1 -T 5 -I -J zap-report.json -r zap-report.html -x zap-report.xml 1> reports\dast\zap.log 2>&1
docker logs pai4-app-dast 1> reports\dast\app.log 2>&1
```

### Importante sobre el código de salida

En local, ZAP puede devolver código no cero aunque el escaneo sea válido, simplemente porque ha encontrado warnings. Eso no invalida la prueba.

Lo que manda aquí es:

- que se generen los reportes
- que `zap.log` contenga hallazgos reales

### Artefactos esperados

- `reports\dast\zap-report.html`
- `reports\dast\zap-report.json`
- `reports\dast\zap-report.xml`
- `reports\dast\zap.log`

### Qué hallazgos debes esperar

Como mínimo, findings del estilo:

- falta de cabeceras de seguridad
- ausencia de anti-CSRF
- XSS reflejado en `/legacy/search`

### Verificación rápida

```powershell
Get-Content reports\dast\zap.log
```

Debes ver referencias a:

- `Cross Site Scripting (Reflected)`
- `/legacy/search`

## 11. Validar la gestión de vulnerabilidades

### Qué se está comprobando

Que existe el intento real de integración con DefectDojo y que, si no hay credenciales, la limitación queda documentada.

### Ejecutar la comprobación sin credenciales

```powershell
$cwd = (Get-Location).Path
docker run --rm -v "${cwd}:/work" -w /work --entrypoint sh curlimages/curl:8.11.1 scripts/run_defectdojo.sh
```

### Resultado esperado si no has configurado DefectDojo

Deben aparecer:

- `reports\vulnerability-management\README.md`
- `reports\vulnerability-management\attempts.tsv`

Y en `README.md` debe quedar explicado que no hubo import real por falta de:

- `DEFECTDOJO_URL`
- `DEFECTDOJO_API_TOKEN`

### Si quieres probar integración real

Debes definir variables de entorno o variables de CI:

```powershell
$env:DEFECTDOJO_URL="https://tu-instancia-defectdojo"
$env:DEFECTDOJO_API_TOKEN="tu-token"
```

Después vuelves a ejecutar el script.

## 12. Comprobar que los artefactos finales existen

Ejecuta:

```powershell
Get-ChildItem reports -Recurse -File
```

Debes ver al menos:

| Ruta | Debe existir |
| --- | --- |
| `reports\sca\pip-audit-report.json` | Sí |
| `reports\sast\semgrep.json` | Sí |
| `reports\iac\trivy-iac-report.json` | Sí |
| `reports\tests\pytest-report.json` | Sí |
| `reports\build\docker-build.log` | Sí |
| `reports\deploy\healthcheck.json` | Sí |
| `reports\dast\zap-report.json` | Sí |
| `reports\vulnerability-management\README.md` | Sí |

## 13. Comprobación rápida final

Si quieres una verificación corta antes de entregar, sigue este orden:

1. `python -m venv .venv`
2. `.\.venv\Scripts\python -m pip install -r requirements.txt`
3. ejecutar `pytest`
4. ejecutar SCA
5. ejecutar SAST
6. ejecutar IaC
7. construir imagen Docker
8. levantar contenedor y verificar `/health`
9. ejecutar ZAP
10. comprobar que `reports/` tiene todos los artefactos

## 14. Qué significa que todo esté bien

La entrega está “bien” cuando se cumplen simultáneamente estas condiciones:

| Condición | Estado correcto |
| --- | --- |
| Estructura | todos los archivos están en `Nuevo/` |
| Tests | pasan los 9 tests |
| SCA | detecta vulnerabilidades reales |
| SAST | detecta el uso inseguro de `Markup(query)` |
| IaC | detecta la mala práctica del Dockerfile |
| Build | crea la imagen sin error |
| Deploy | el contenedor responde en `/health` |
| DAST | ZAP genera reportes con hallazgos |
| DefectDojo | hay intento documentado o import real si pones credenciales |
| Documentación | `README.md`, `Informe-PAI4.md` y este manual existen |

## 15. Limpieza final opcional

Cuando termines, puedes dejar el entorno limpio así:

```powershell
docker rm -f pai4-app pai4-app-dast
docker network rm pai4-net pai4-zap-net
Remove-Item -Recurse -Force .venv,.audit-venv
```

Si alguna red no existe, PowerShell puede mostrar aviso; no pasa nada.

## 16. Qué enseñar al profesor

Si te piden demostrarlo rápido, enseña esto:

1. la estructura de `Nuevo/`
2. `pytest` con `9 passed`
3. `reports\sca\pip-audit.txt`
4. `reports\sast\semgrep.txt`
5. `reports\iac\trivy-iac.txt`
6. `reports\deploy\healthcheck.json`
7. `reports\dast\zap-report.html`
8. `Informe-PAI4.md`

Con eso demuestras:

- pipeline preparada
- controles de seguridad verificados
- hallazgos reales
- trazabilidad
- documentación
