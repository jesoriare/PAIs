# PAI 4. DevSecOps - ASEGURAMIENTO DE LA CADENA DE SUMINISTRO EN EL DESARROLLO DE APLICACIONES WEB

## Introducción

Una entidad de desarrollo de aplicaciones Web, que es cliente de INSEGUS ha experimentado recientemente varios incidentes de seguridad debido a vulnerabilidades en sus sistemas debido a tráfico malicioso en la red.

Para mejorar su postura de seguridad, la empresa ha decidido implementar un enfoque DevSecOps utilizando diferentes herramientas de automatización.

Actualmente la empresa sigue para sus desarrollos un Pipeline de integración y despliegue continuo (CI/CD).

Además, en dicha entidad se complica el escenario para llevar a cabo los tests de seguridad, si pensamos que el desarrollo se está pasando al escenario de aplicaciones software monolíticas a aplicaciones basadas en microservicios, con el consiguiente aumento de la superficie de ataque.

Y además estos microservicios están siendo ejecutados en Containers, por lo tanto, mucho más aumento de la superficie de ataque, a lo que se añade las plataformas de nubes públicas que usan y además de utilizar Kubernetes para administrar las aplicaciones en contenedores.

Todo ello ha llevado a la empresa plantearse acudir a la automatización de lo que serían las actividades de análisis y mitigación de dichos ciberriesgos durante el desarrollo y despliegue en producción.

Por tanto, dado el proceso de DevOps automatizado que es llevado a cabo actualmente en la empresa requiere también que los test de seguridad se hagan de forma automatizada a lo largo de todo el Pipeline del ciclo de desarrollo.

La propuesta es usar un esquema DevSecOps.

---

## Objetivos del proyecto

1. Definir una Pipeline CI/CD en un proyecto de prueba en un repositorio de código (SCM).

2. Seleccionar al menos tres herramientas de Testeo de Seguridad (SCA, SAST, IAST, DAST, Security IaC).

3. Integrar las herramientas de Testeo en el ciclo de vida del desarrollo.

4. Desarrollar los tests correspondientes que permitan detectar vulnerabilidades en cada etapa del Pipeline DevSecOp.

5. Seleccionar una herramienta de gestión de vulnerabilidades para integrar, priorizar y clasificar vulnerabilidades.

---

## Recomendaciones

### Pipelines CI/CD
- GitLab CI/CD
- GitHub CI/CD
- Jenkins

### SCA
- Dependabot
- Snyk
- OWASP Dependency-Check
- Sonatype Nexus

### SAST
- SonarQube
- OWASP Source Code Analysis Tools

### IAST
- Semgrep
- RIPS
- Contrast Security

### DAST
- OWASP ZAP
- Burp Suite
- Wapiti

### IaC
- KICS
- Trivy
- Terrascan

---

## Gestión de vulnerabilidades

- DefectDojo

---

## Normas del entregable

Entrega en ZIP: `PAI4-STX.zip`

Debe contener:
- Código fuente
- Scripts/configuración
- Tests y logs
- Informe técnico (PDF máximo 10 páginas)

### Estructura del PDF

- Informe técnico
- Manual de despliegue y uso
- Grado de completitud

### Fecha límite
27 de abril, 23:59

### Penalizaciones
- 10% por día de retraso
- No se aceptan entregas por email