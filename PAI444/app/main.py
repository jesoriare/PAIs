from __future__ import annotations

import os
import secrets
from decimal import Decimal, InvalidOperation
from functools import wraps
from pathlib import Path

from flask import Flask, abort, current_app, jsonify, redirect, render_template, request, session, url_for
from markupsafe import Markup
from werkzeug.security import check_password_hash

from .db import add_comment, get_user_by_id, get_user_by_username, init_db, list_comments


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "app.db"
CATALOG = {
    "SKU-BOOK": {"name": "Secure Coding Book", "price": Decimal("15.00")},
    "SKU-LAB": {"name": "Container Security Lab", "price": Decimal("30.00")},
}


def get_current_user():
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return get_user_by_id(current_app.config["DATABASE_PATH"], int(user_id))


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if get_current_user() is None:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def role_required(*allowed_roles: str):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = get_current_user()
            if user is None:
                return redirect(url_for("login", next=request.path))
            if user["role"] not in allowed_roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def _safe_redirect_target(candidate: str | None) -> str:
    if candidate and candidate.startswith("/") and not candidate.startswith("//"):
        return candidate
    return url_for("dashboard")


def _validate_comment(message: str) -> str:
    normalized = message.strip()
    if not 1 <= len(normalized) <= 200:
        abort(400)
    return normalized


def _validate_checkout_items(raw_items):
    if not isinstance(raw_items, list) or not raw_items:
        abort(400)

    validated_items = []
    for raw_item in raw_items:
        if not isinstance(raw_item, dict):
            abort(400)

        sku = raw_item.get("sku")
        if sku not in CATALOG:
            abort(400)

        quantity = raw_item.get("quantity")
        if not isinstance(quantity, int) or quantity < 1 or quantity > 10:
            abort(400)

        validated_items.append(
            {
                "sku": sku,
                "name": CATALOG[sku]["name"],
                "quantity": quantity,
                "unit_price": CATALOG[sku]["price"],
            }
        )

    return validated_items


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.config.update(
        SECRET_KEY=os.getenv("PAI4_SECRET_KEY") or secrets.token_hex(32),
        DATABASE_PATH=os.getenv("PAI4_DB_PATH", str(DEFAULT_DB_PATH)),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    if test_config:
        app.config.update(test_config)

    init_db(app.config["DATABASE_PATH"])

    @app.get("/")
    def index():
        return render_template("index.html", user=get_current_user(), catalog=CATALOG)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = get_user_by_username(app.config["DATABASE_PATH"], username)

            if user is None or not check_password_hash(user["password_hash"], password):
                return render_template("login.html", next_target=request.args.get("next")), 401

            session.clear()
            session["user_id"] = user["id"]
            return redirect(_safe_redirect_target(request.args.get("next")))

        return render_template("login.html", next_target=request.args.get("next"))

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    @app.get("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html", user=get_current_user())

    @app.get("/admin/audit")
    @role_required("admin")
    def admin_audit():
        user = get_current_user()
        return jsonify(
            {
                "username": user["username"],
                "role": user["role"],
                "review_state": "restricted",
            }
        )

    @app.get("/profile")
    @login_required
    def profile():
        user = get_current_user()
        capabilities = ["feedback:write", "checkout:submit"]
        if user["role"] == "admin":
            capabilities.append("audit:read")

        return jsonify(
            {
                "username": user["username"],
                "role": user["role"],
                "capabilities": capabilities,
            }
        )

    @app.route("/feedback", methods=["GET", "POST"])
    @login_required
    def feedback():
        user = get_current_user()
        if request.method == "POST":
            message = _validate_comment(request.form.get("message", ""))
            add_comment(app.config["DATABASE_PATH"], user["username"], message)
            return redirect(url_for("feedback"))

        return render_template("feedback.html", user=user, comments=list_comments(app.config["DATABASE_PATH"]))

    @app.post("/checkout")
    @login_required
    def checkout():
        payload = request.get_json(silent=True)
        if payload is None:
            abort(400)

        validated_items = _validate_checkout_items(payload.get("items"))
        submitted_total = payload.get("client_total")
        try:
            submitted_total_decimal = Decimal(str(submitted_total))
        except (InvalidOperation, TypeError):
            submitted_total_decimal = None

        server_total = sum(item["unit_price"] * item["quantity"] for item in validated_items)
        return jsonify(
            {
                "server_total": f"{server_total:.2f}",
                "submitted_total": None if submitted_total_decimal is None else f"{submitted_total_decimal:.2f}",
                "client_total_accepted": False,
                "line_items": [
                    {
                        "sku": item["sku"],
                        "name": item["name"],
                        "quantity": item["quantity"],
                        "unit_price": f"{item['unit_price']:.2f}",
                    }
                    for item in validated_items
                ],
            }
        )

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/legacy/search")
    def legacy_search():
        query = request.args.get("q", "")
        # Intentionally unsafe legacy rendering retained to demonstrate scanner detection.
        return render_template("legacy.html", query=Markup(query), user=get_current_user())

    return app


app = create_app()
