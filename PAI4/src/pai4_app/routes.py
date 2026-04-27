import os
import subprocess

from flask import Blueprint, jsonify, request


bp = Blueprint("api", __name__)

DEMO_USER = os.getenv("PAI4_USER", "security-team")
DEMO_PASSWORD = os.getenv("PAI4_PASSWORD", "ChangeMe123!")

PRODUCTS = [
    {"id": 1, "name": "Monitor de vuelo", "price": 199.99},
    {"id": 2, "name": "Router de cabina", "price": 349.50},
    {"id": 3, "name": "Gateway ZTNA", "price": 799.00},
]


@bp.get("/")
def home():
    return jsonify(
        {
            "service": "PAI4 DevSecOps Demo",
            "status": "ok",
            "message": "Aplicacion web de prueba para pipeline DevSecOps.",
        }
    )


@bp.get("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@bp.get("/products")
def products():
    return jsonify({"items": PRODUCTS, "count": len(PRODUCTS)})


@bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = payload.get("username", "")
    password = payload.get("password", "")

    if not username or not password:
        return jsonify({"error": "username y password son obligatorios"}), 400

    if username == DEMO_USER and password == DEMO_PASSWORD:
        return jsonify({"message": "login correcto", "token": "demo-token"}), 200

    return jsonify({"error": "credenciales invalidas"}), 401


@bp.get("/admin/diagnostic")
def diagnostic():
    # Endpoint deliberadamente inseguro para que SAST detecte command injection.
    host = request.args.get("host", "127.0.0.1")
    result = subprocess.run(
        f"ping -c 1 {host}",
        shell=True,
        capture_output=True,
        text=True,
        timeout=3,
    )
    return jsonify({"returncode": result.returncode, "output": result.stdout[:200]})
