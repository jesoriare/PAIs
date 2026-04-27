# Manual de Verificacion

## Objetivo

Este documento explica como comprobar que la version final del proyecto en `PAI4/` funciona y que las evidencias coinciden con lo pedido en el enunciado.

## Requisitos previos

- Python 3.11 o superior
- Docker Desktop iniciado
- acceso a Internet para descargar imagenes y dependencias

## 1. Estructura del proyecto

En la raiz de `PAI4/` deben existir como minimo:

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
- `requirements-dev.txt`
- `pytest.ini`

## 2. Preparar entorno Python

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
```

## 3. Ejecutar tests

```powershell
$env:PYTHONPATH='.'
.\.venv\Scripts\python -m pytest --junitxml=reports\tests\pytest-junit.xml --json-report --json-report-file=reports\tests\pytest-report.json tests\security
```

Resultado esperado:

- `9 passed`

## 4. Levantar la aplicacion

```powershell
$env:PAI4_ADMIN_PASSWORD="AdminPassTemporal!123"
$env:PAI4_MEMBER_PASSWORD="MemberPassTemporal!123"
docker compose -f docker\docker-compose.yml up --build
```

Comprobad:

- `http://localhost:5000/`
- `http://localhost:5000/login`
- `http://localhost:5000/health`

## 5. Validar SCA

```powershell
python -m venv .audit-venv
.\.audit-venv\Scripts\python -m pip install --upgrade pip pip-audit
.\.audit-venv\Scripts\pip-audit -r security\sca\requirements-sca.txt --format json 1> reports\sca\pip-audit-report.json 2> reports\sca\pip-audit.log
.\.audit-venv\Scripts\pip-audit -r security\sca\requirements-sca.txt 1> reports\sca\pip-audit.txt 2>> reports\sca\pip-audit.log
```

Debe detectar vulnerabilidades sobre `urllib3==1.25.8`.

## 6. Validar SAST

```powershell
$cwd = (Get-Location).Path
docker run --rm -v "${cwd}:/src" -w /src semgrep/semgrep:1.123.0 sh scripts/run_sast.sh
```

Debe aparecer el hallazgo sobre `Markup(query)` en `app/main.py`.

## 7. Validar IaC

```powershell
$cwd = (Get-Location).Path
docker run --rm --entrypoint sh -v "${cwd}:/work" -w /work aquasec/trivy:0.65.0 scripts/run_iac.sh
```

Debes comprobar que la imagen no se ejecuta como `root` y que el Dockerfile sigue endurecido.

## 8. Validar Build y Deploy

```powershell
docker build -f docker/Dockerfile -t pai4-app:ci . 1> reports\build\docker-build.log 2>&1
docker image inspect pai4-app:ci | Out-File -FilePath reports\build\image-inspect.json -Encoding utf8
```

```powershell
$adminPass = 'admin-' + [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$memberPass = 'member-' + [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
docker network create pai4-net 1> reports\deploy\network.log 2>&1
docker rm -f pai4-app *> $null
docker run -d --name pai4-app --network pai4-net -p 5000:5000 -e PAI4_DB_PATH=/opt/pai4/data/app.db -e PAI4_ADMIN_USERNAME=admin -e PAI4_MEMBER_USERNAME=member -e PAI4_ADMIN_PASSWORD=$adminPass -e PAI4_MEMBER_PASSWORD=$memberPass pai4-app:ci | Out-File -FilePath reports\deploy\container-id.txt -Encoding ascii
Start-Sleep -Seconds 10
docker run --rm --network pai4-net curlimages/curl:8.11.1 curl -fsS http://pai4-app:5000/health | Out-File -FilePath reports\deploy\healthcheck.json -Encoding ascii
```

## 9. Validar DAST

```powershell
$adminPass = 'admin-' + [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$memberPass = 'member-' + [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
docker network create pai4-zap-net 1> reports\dast\network.log 2>&1
docker rm -f pai4-app-dast *> $null
docker run -d --name pai4-app-dast --network pai4-zap-net -e PAI4_DB_PATH=/opt/pai4/data/app.db -e PAI4_ADMIN_USERNAME=admin -e PAI4_MEMBER_USERNAME=member -e PAI4_ADMIN_PASSWORD=$adminPass -e PAI4_MEMBER_PASSWORD=$memberPass pai4-app:ci | Out-File -FilePath reports\dast\container-id.txt -Encoding ascii
Start-Sleep -Seconds 10
docker run --rm --network pai4-zap-net -v "${PWD}\reports\dast:/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable zap-full-scan.py -t http://pai4-app-dast:5000 -m 1 -T 5 -I -J zap-report.json -r zap-report.html -x zap-report.xml 1> reports\dast\zap.log 2>&1
```

## 10. DefectDojo

Sin credenciales:

```powershell
$cwd = (Get-Location).Path
docker run --rm -v "${cwd}:/work" -w /work --entrypoint sh curlimages/curl:8.11.1 scripts/run_defectdojo.sh
```

Debe quedar trazabilidad en `reports/vulnerability-management/`.

## 11. Comprobacion final

La entrega esta lista cuando:

- los 9 tests pasan
- SCA, SAST, IaC y DAST generan reportes
- `/health` responde correctamente
- `reports/` contiene las evidencias principales
- `README.md`, `Informe-PAI4.md` y este manual describen la misma version

## 12. ZIP final

Antes de comprimir:

1. regenera `reports/` si has cambiado codigo o configuracion
2. incluye solo el contenido de `PAI4/`
3. genera el ZIP con el nombre pedido por el enunciado
