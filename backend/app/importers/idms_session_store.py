import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional


class IdmsSessionStore:
    """Guarda y recupera cookies de sesión de IDMS en disco."""

    def __init__(self, path: str = "data/idms_session.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, cookies: Dict[str, str], ttl_days: int = 30) -> dict:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=ttl_days)
        payload = {
            "cookies": cookies,
            "created_at": now.isoformat(),
            "expires_at": expires.isoformat(),
            "ttl_days": ttl_days,
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        os.chmod(self.path, 0o600)
        return payload

    def load(self) -> Optional[dict]:
        if not self.path.exists():
            return None
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def cookies(self) -> Dict[str, str]:
        data = self.load()
        if data and isinstance(data.get("cookies"), dict):
            return data["cookies"]
        return {}

    def session_info(self) -> Optional[dict]:
        data = self.load()
        if not data:
            return None
        try:
            created = datetime.fromisoformat(data["created_at"])
            expires = datetime.fromisoformat(data["expires_at"])
        except (KeyError, ValueError):
            return None
        remaining = (expires - datetime.now(timezone.utc)).total_seconds() / 86400
        return {
            "created_at": created.isoformat(),
            "expires_at": expires.isoformat(),
            "days_remaining": max(0, int(remaining)),
            "expired": remaining <= 0,
        }

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()
