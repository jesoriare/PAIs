# Manual de despliegue y uso

## Requisitos

- Python 3.11
- Docker
- GitLab CI/CD o entorno equivalente

## Instalacion local

```powershell
cd PAI4
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python app.py
```

## Ejecucion con Docker

```powershell
docker build -t pai4-devsecops .
docker run --rm -p 5000:5000 pai4-devsecops
```

## DAST local con Docker

Con la aplicacion arrancada en `http://127.0.0.1:5000`:

```powershell
New-Item -ItemType Directory -Force reports\dast
docker run --rm -t -v "${PWD}\\reports\\dast:/zap/wrk" owasp/zap2docker-stable zap-baseline.py -t http://host.docker.internal:5000 -J /zap/wrk/zap-report.json
```

## Flujo esperado del pipeline

1. `SCA` analiza dependencias
2. `SAST` analiza codigo fuente Python
3. `IaC` analiza Dockerfile y configuraciones
4. `Test` ejecuta pruebas unitarias
5. `Build` construye la imagen
6. `DAST` analiza la app en ejecucion
7. `Vulnerability-Management` importa resultados si DefectDojo esta configurado
