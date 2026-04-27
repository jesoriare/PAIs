from __future__ import annotations

import os
import sys
from pathlib import Path

from werkzeug.security import generate_password_hash


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db import init_db, upsert_user  # noqa: E402


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def main() -> None:
    db_path = os.getenv("PAI4_DB_PATH", str(ROOT_DIR / "data" / "app.db"))
    admin_username = os.getenv("PAI4_ADMIN_USERNAME", "admin")
    member_username = os.getenv("PAI4_MEMBER_USERNAME", "member")
    admin_password = required_env("PAI4_ADMIN_PASSWORD")
    member_password = required_env("PAI4_MEMBER_PASSWORD")

    init_db(db_path)
    upsert_user(db_path, admin_username, generate_password_hash(admin_password), "admin")
    upsert_user(db_path, member_username, generate_password_hash(member_password), "member")
    print(f"Bootstrapped users into {db_path}")


if __name__ == "__main__":
    main()
