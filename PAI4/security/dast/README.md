# DAST scope

`OWASP ZAP` performs a packaged full scan against the running container.

The application intentionally exposes `/legacy/search?q=...` with unsafe rendering, and the app also omits hardening headers so the DAST stage can generate observable findings in `reports/dast/`.
