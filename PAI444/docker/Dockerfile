FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/pai4

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app app
COPY scripts scripts

RUN useradd --create-home --uid 10001 appuser && \
    mkdir -p /opt/pai4/data && \
    chown -R appuser:appuser /opt/pai4

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:5000/health', timeout=3).read()"

CMD ["sh", "-c", "python scripts/bootstrap_users.py && gunicorn --bind 0.0.0.0:5000 app.main:app"]
