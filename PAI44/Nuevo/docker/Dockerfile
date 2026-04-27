FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/pai4

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app app
COPY scripts scripts

EXPOSE 5000

CMD ["sh", "-c", "python scripts/bootstrap_users.py && gunicorn --bind 0.0.0.0:5000 app.main:app"]
