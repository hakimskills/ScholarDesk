# -*- coding: utf-8 -*-
"""
app/sms_gateway_config.py

Connection details for the local Android SMS gateway (base URL,
credentials) — kept as a small JSON file next to the SQLite database
rather than baked into message_service.py, since this is app
configuration (which phone, which network) rather than school data.

This module is provider-agnostic on purpose: it only stores/loads
the connection details. app/services/message_service.py is where the
actual HTTP request format for whichever gateway app you use gets
implemented — that's the one piece still pending your app's exact
API shape.

Later, a "الإعدادات" settings page (already a placeholder tile on the
dashboard) can read/write this via load_config()/save_config()
instead of hand-editing the JSON file.
"""

import json
import os
from dataclasses import dataclass, asdict

from app.database import DATA_DIR

_CONFIG_PATH = os.path.join(DATA_DIR, "sms_gateway_config.json")


@dataclass
class SmsGatewayConfig:
    enabled: bool = False      # off by default until someone configures + turns it on
    base_url: str = ""         # e.g. "http://192.168.1.50:8080"
    username: str = ""         # Basic Auth, if the gateway app requires it
    password: str = ""
    timeout_seconds: int = 15  # per-request network timeout


def load_config() -> SmsGatewayConfig:
    """Read the saved config, or return safe defaults (disabled,
    empty) if nothing's been configured yet or the file is corrupt."""
    if not os.path.exists(_CONFIG_PATH):
        return SmsGatewayConfig()
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return SmsGatewayConfig(**{
            field: data[field] for field in SmsGatewayConfig.__dataclass_fields__ if field in data
        })
    except (json.JSONDecodeError, OSError, TypeError):
        return SmsGatewayConfig()


def save_config(config: SmsGatewayConfig) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(asdict(config), f, ensure_ascii=False, indent=2)