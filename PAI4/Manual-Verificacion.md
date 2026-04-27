# Manual de VerificaciÃ³n Completa

## Objetivo

Este documento explica, paso a paso y sin asumir contexto previo, cÃ³mo comprobar que el proyecto `PAI-4` de la carpeta `PAI44/` estÃ¡ correcto, que los controles de seguridad funcionan, que la aplicaciÃ³n arranca, que los artefactos se generan y que las evidencias coinciden con lo que exige el enunciado.

La idea es que puedas usar este manual para:

- validar la entrega antes de comprimirla
- repetir las pruebas si cambias algo
- demostrar al profesor que la soluciÃ³n es reproducible
- saber quÃ© resultado esperar en cada fase

## QuÃ© se va a comprobar

La validaciÃ³n completa cubre estas Ã¡reas:

| Ãrea | QuÃ© se comprueba |
| --- | --- |
| Estructura | Que `PAI44/` contiene todos los ficheros y carpetas exigidos |
| AplicaciÃ³n | Que la app Flask arranca y responde |
| Tests | Que los tests de seguridad pasan |
| SCA | Que `pip-audit` detecta vulnerabilidades reales |
| SAST | Que Semgrep detecta el patrÃ³n inseguro intencional |
| IaC | Que Trivy detecta malas prÃ¡cticas en el Dockerfile |
| Build | Que la imagen Docker se construye correctamente |
| Deploy | Que el contenedor queda levantado y el healthcheck responde |
| DAST | Que ZAP encuentra hallazgos reales contra la app en ejecuciÃ³n |
| GestiÃ³n de vulnerabilidades | Que existe el intento de integraciÃ³n con DefectDojo y queda trazabilidad |

## Antes de empezar

### Ruta de trabajo

Abre PowerShell y sitÃºate aquÃ­:

```powershell
cd C:\\ruta\\hasta\\PAI44
```

Todas las Ã³rdenes de este documento asumen esa ruta.

### Requisitos previos

Debes tener disponible:

- Python 3.11 o superior
- Docker Desktop arrancado
- acceso a Internet para descargar imÃ¡genes Docker y paquetes Python

### Comprobaciones iniciales

Ejecuta:

```powershell
python --version
docker --version
docker info
```

QuÃ© debes esperar:

- `python --version` devuelve una versiÃ³n vÃ¡lida
- `docker --version` devuelve versiÃ³n instalada
- `docker info` no da error y confirma que Docker Desktop estÃ¡ levantado

Si `docker info` falla:

1. abre Docker Desktop
2. espera a que indique que estÃ¡ listo
3. vuelve a lanzar `docker info`

## 1. Comprobar la estructura del proyecto

### QuÃ© hacer

Ejecuta:

```powershell
Get-ChildItem -Force
```

### QuÃ© debe existir en la raÃ­z de `PAI44/`

Debes ver como mÃ­nimo:

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

### VerificaciÃ³n adicional

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

Si falta alguno de esos archivos, no sigas con la verificaciÃ³n: primero habrÃ­a que corregir la estructura.

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
.\\.venv\\Scripts\\python -m pip install -r requirements-dev.txt
```

### QuÃ© debes esperar

- instalaciÃ³n correcta sin errores
- paquetes principales instalados:
  `Flask`, `gunicorn`, `pytest`, `pytest-json-report`

## 3. Ejecutar y validar los tests de seguridad

### Ejecutar tests

Ejecuta:

```powershell
$env:PYTHONPATH='.'
.\.venv\Scripts\python -m pytest --junitxml=reports\tests\pytest-junit.xml --json-report --json-report-file=reports\tests\pytest-report.json tests\security
```

### QuÃ© debes esperar

El resultado correcto es:

```text
9 passed
```

### QuÃ© controles estÃ¡n cubiertos

| Test | QuÃ© valida |
| --- | --- |
| `test_dashboard_requires_login` | que no se entra al dashboard sin login |
| `test_successful_login_sets_session_and_redirects_to_dashboard` | que el login correcto crea sesiÃ³n |
| `test_member_cannot_access_admin_route` | que un usuario normal no entra a la ruta admin |
| `test_admin_can_access_admin_route` | que un admin sÃ­ puede entrar |
| `test_feedback_rejects_overlong_input` | que la entrada excesiva se bloquea |
| `test_checkout_rejects_invalid_quantities` | que cantidades invÃ¡lidas se rechazan |
| `test_feedback_output_is_escaped` | que el contenido del usuario se escapa y no se ejecuta |
| `test_profile_omits_password_material` | que no se expone material sensible |
| `test_checkout_total_is_calculated_server_side` | que el total lo calcula el servidor |

### Artefactos a revisar

DespuÃ©s de ejecutar los tests deben existir:

- `reports\tests\pytest.log`
- `reports\tests\pytest-junit.xml`
- `reports\tests\pytest-report.json`

### VerificaciÃ³n rÃ¡pida de artefactos

```powershell
Get-ChildItem reports\tests
Get-Content reports\tests\pytest.log
```

Debes ver al final del log una lÃ­nea equivalente a:

```text
9 passed
```

## 4. Validar la aplicaciÃ³n manualmente

Esta parte sirve para comprobar la aplicaciÃ³n sin scanners, como si fueras un usuario.

### Levantar la app con Docker Compose

Ejecuta:

```powershell
$env:PAI4_ADMIN_PASSWORD="AdminPassTemporal!123"
$env:PAI4_MEMBER_PASSWORD="MemberPassTemporal!123"
docker compose -f docker\docker-compose.yml up --build
```

DÃ©jalo arrancado.

### QuÃ© debes esperar en consola

Mensajes parecidos a:

- instalaciÃ³n de dependencias
- `Bootstrapped users into /opt/pai4/data/app.db`
- `Starting gunicorn`
- `Listening at: http://0.0.0.0:5000`

### QuÃ© comprobar en navegador

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

### QuÃ© comprobar manualmente con lÃ³gica de seguridad

#### Comprobar autenticaciÃ³n

1. abre `http://localhost:5000/dashboard`
2. sin haber iniciado sesiÃ³n, debe redirigir al login

#### Comprobar autorizaciÃ³n

Este flujo estÃ¡ mejor cubierto por tests, pero puedes validarlo asÃ­:

1. inicia sesiÃ³n con un usuario normal si adaptas el formulario a tus credenciales creadas por entorno
2. intenta acceder a `/admin/audit`
3. debe devolver `403`

#### Comprobar validaciÃ³n

1. entra a `/feedback` tras login
2. envÃ­a un mensaje normal
3. debe guardarse
4. si modificas manualmente el formulario para mandar mÃ¡s de 200 caracteres, debe rechazarse

#### Comprobar integridad de negocio

La comprobaciÃ³n fuerte la hacen los tests, pero la lÃ³gica del endpoint `/checkout` estÃ¡ pensada para ignorar el total enviado por el cliente y calcular el suyo propio.

### Parar la aplicaciÃ³n

En la misma terminal:

```powershell
Ctrl + C
docker compose -f docker\docker-compose.yml down
```

## 5. Ejecutar y validar SCA

### QuÃ© se estÃ¡ comprobando

`pip-audit` escanea `security\sca\requirements-sca.txt`.

Ese fichero aÃ±ade intencionalmente:

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

### QuÃ© debes esperar

No esperes un â€œtodo limpioâ€. AquÃ­ lo correcto es que encuentre vulnerabilidades.

Como mÃ­nimo debe haber findings sobre `urllib3==1.25.8`.

### Artefactos esperados

- `reports\sca\pip-audit-report.json`
- `reports\sca\pip-audit.txt`
- `reports\sca\pip-audit.log`

### VerificaciÃ³n rÃ¡pida

```powershell
Get-Content reports\sca\pip-audit.txt
```

Debes ver referencias a `urllib3 1.25.8` y sus fixes recomendados.

## 6. Ejecutar y validar SAST

### QuÃ© se estÃ¡ comprobando

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

### QuÃ© debes esperar

No debe salir â€œ0 findingsâ€. Lo correcto es que aparezca 1 hallazgo.

### Artefactos esperados

- `reports\sast\semgrep.json`
- `reports\sast\semgrep.txt`
- `reports\sast\semgrep.log`

### VerificaciÃ³n rÃ¡pida

```powershell
Get-Content reports\sast\semgrep.txt
```

Debes ver un finding sobre:

- `security.sast.flask-legacy-markup-user-input`
- `app/main.py`

## 7. Ejecutar y validar IaC

### QuÃ© se estÃ¡ comprobando

Trivy analiza:

- `docker\Dockerfile`

El Dockerfile contiene a propÃ³sito una mala prÃ¡ctica:

- no define usuario no root con `USER`

TambiÃ©n puede detectar:

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

### VerificaciÃ³n rÃ¡pida

```powershell
Get-Content reports\iac\trivy-iac.txt
```

Debes ver como mÃ­nimo:

- `DS-0002` por falta de usuario no root

Puede aparecer tambiÃ©n:

- `DS-0026` por falta de `HEALTHCHECK`

## 8. Ejecutar y validar Build

### QuÃ© se estÃ¡ comprobando

Que la imagen Docker de la aplicaciÃ³n se construye correctamente.

### Ejecutar Build

```powershell
docker build -f docker/Dockerfile -t pai4-app:ci . 1> reports\build\docker-build.log 2>&1
docker image inspect pai4-app:ci | Out-File -FilePath reports\build\image-inspect.json -Encoding utf8
```

### QuÃ© debes esperar

- build sin errores
- imagen `pai4-app:ci` creada

### VerificaciÃ³n rÃ¡pida

```powershell
docker images | Select-String pai4-app
Get-Content reports\build\docker-build.log
```

## 9. Ejecutar y validar Deploy

### QuÃ© se estÃ¡ comprobando

Que la imagen reciÃ©n construida arranca como contenedor y responde a `/health`.

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

| ComprobaciÃ³n | Resultado esperado |
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

### QuÃ© se estÃ¡ comprobando

Que ZAP escanea la aplicaciÃ³n en ejecuciÃ³n y detecta hallazgos reales.

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

### Importante sobre el cÃ³digo de salida

En local, ZAP puede devolver cÃ³digo no cero aunque el escaneo sea vÃ¡lido, simplemente porque ha encontrado warnings. Eso no invalida la prueba.

Lo que manda aquÃ­ es:

- que se generen los reportes
- que `zap.log` contenga hallazgos reales

### Artefactos esperados

- `reports\dast\zap-report.html`
- `reports\dast\zap-report.json`
- `reports\dast\zap-report.xml`
- `reports\dast\zap.log`

### QuÃ© hallazgos debes esperar

Como mÃ­nimo, findings del estilo:

- falta de cabeceras de seguridad
- ausencia de anti-CSRF
- XSS reflejado en `/legacy/search`

### VerificaciÃ³n rÃ¡pida

```powershell
Get-Content reports\dast\zap.log
```

Debes ver referencias a:

- `Cross Site Scripting (Reflected)`
- `/legacy/search`

## 11. Validar la gestiÃ³n de vulnerabilidades

### QuÃ© se estÃ¡ comprobando

Que existe el intento real de integraciÃ³n con DefectDojo y que, si no hay credenciales, la limitaciÃ³n queda documentada.

### Ejecutar la comprobaciÃ³n sin credenciales

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

### Si quieres probar integraciÃ³n real

Debes definir variables de entorno o variables de CI:

```powershell
$env:DEFECTDOJO_URL="https://tu-instancia-defectdojo"
$env:DEFECTDOJO_API_TOKEN="tu-token"
```

DespuÃ©s vuelves a ejecutar el script.

## 12. Comprobar que los artefactos finales existen

Ejecuta:

```powershell
Get-ChildItem reports -Recurse -File
```

Debes ver al menos:

| Ruta | Debe existir |
| --- | --- |
| `reports\sca\pip-audit-report.json` | SÃ­ |
| `reports\sast\semgrep.json` | SÃ­ |
| `reports\iac\trivy-iac-report.json` | SÃ­ |
| `reports\tests\pytest-report.json` | SÃ­ |
| `reports\build\docker-build.log` | SÃ­ |
| `reports\deploy\healthcheck.json` | SÃ­ |
| `reports\dast\zap-report.json` | SÃ­ |
| `reports\vulnerability-management\README.md` | SÃ­ |

## 13. ComprobaciÃ³n rÃ¡pida final

Si quieres una verificaciÃ³n corta antes de entregar, sigue este orden:

1. `python -m venv .venv`
2. `.\\.venv\\Scripts\\python -m pip install -r requirements-dev.txt`
3. ejecutar `pytest`
4. ejecutar SCA
5. ejecutar SAST
6. ejecutar IaC
7. construir imagen Docker
8. levantar contenedor y verificar `/health`
9. ejecutar ZAP
10. comprobar que `reports/` tiene todos los artefactos

## 14. QuÃ© significa que todo estÃ© bien

La entrega estÃ¡ â€œbienâ€ cuando se cumplen simultÃ¡neamente estas condiciones:

| CondiciÃ³n | Estado correcto |
| --- | --- |
| Estructura | todos los archivos estÃ¡n en `PAI44/` |
| Tests | pasan los 9 tests |
| SCA | detecta vulnerabilidades reales |
| SAST | detecta el uso inseguro de `Markup(query)` |
| IaC | detecta la mala prÃ¡ctica del Dockerfile |
| Build | crea la imagen sin error |
| Deploy | el contenedor responde en `/health` |
| DAST | ZAP genera reportes con hallazgos |
| DefectDojo | hay intento documentado o import real si pones credenciales |
| DocumentaciÃ³n | `README.md`, `Informe-PAI4.md` y este manual existen |

## 15. Limpieza final opcional

Cuando termines, puedes dejar el entorno limpio asÃ­:

```powershell
docker rm -f pai4-app pai4-app-dast
docker network rm pai4-net pai4-zap-net
Remove-Item -Recurse -Force .venv,.audit-venv
```

Si alguna red no existe, PowerShell puede mostrar aviso; no pasa nada.

## 16. QuÃ© enseÃ±ar al profesor

Si te piden demostrarlo rÃ¡pido, enseÃ±a esto:

1. la estructura de `PAI44/`
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
- documentaciÃ³n

