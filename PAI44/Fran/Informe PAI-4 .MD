# Informe PAI-4

Seguridad en Sistemas Informáticos e Internet  
Security Team 4  
Adrián Robles Borrego  
Francisco Manuel Sabido Gonzalez  
Jesús Salas Muñoz  

---

## Resumen ejecutivo

Este informe detalla la implementación de un pipeline CI/CD orientado a la seguridad.

Pipeline basado en GitLab CI/CD con herramientas:
- SonarQube
- Trivy
- OWASP ZAP
- DefectDojo

Se automatiza el análisis de seguridad en distintas fases del ciclo de desarrollo.

Fases:
- SCA: pip-audit
- SAST: SonarCloud
- IaC: Trivy
- DAST: OWASP ZAP
- Tests de seguridad automatizados

Problema detectado:
- Fallos en integración con DefectDojo (autenticación y persistencia)

---

## Pipeline CI/CD

Pipeline basado en GitLab CI/CD con fases:

- SCA
- SAST
- IaC
- Test
- Build
- Deploy
- DAST
- Gestión de vulnerabilidades

---

## SCA

### Objetivo
Detectar vulnerabilidades en dependencias.

### Herramienta
pip-audit

### Ejecución
pip-audit --format json > pip-audit-report.json

### Acciones
- Actualizar Django
- Revisar dependencias

---

## SAST

### Objetivo
Detectar vulnerabilidades en código fuente.

### Herramienta
SonarCloud

### Acciones
- Refactorizar código
- Evitar SQL Injection
- Proteger credenciales

---

## IaC

### Objetivo
Detectar malas configuraciones.

### Herramienta
Trivy

### Ejecución
trivy config --format json -o trivy-iac-report.json

### Acciones
- Eliminar credenciales hardcodeadas
- Restringir permisos
- Revisar imágenes Docker

---

## DAST

### Objetivo
Detectar vulnerabilidades en ejecución.

### Herramienta
OWASP ZAP

### Ejecución
zap-baseline.py -t http://host.docker.internal:8080 -J zap-report.json

### Acciones
- Prevenir XSS
- Prevenir SQL Injection
- Configurar cabeceras HTTP

---

## Security Testing

### Objetivo
Automatizar tests de seguridad.

### Implementación
- unittest
- django.test

### Ejecución
Script:
run_security_unit_tests.sh

---

## Build

### Objetivo
Construcción de imagen Docker

### Herramienta
Docker

### Ejecución
docker build -t myapp:latest

---

## Deploy

### Objetivo
Desplegar aplicación para DAST

### Método
Docker container

---

## Gestión de vulnerabilidades

Herramienta: DefectDojo

Integración mediante API REST usando curl.

Problema:
- Fallo de autenticación
- No persistencia de datos

---

## Conclusión

El pipeline permite detectar vulnerabilidades en distintas fases.

Limitación:
- Problemas en DefectDojo impiden integración completa