"""Identifier generation.

Source: compiler/00_core/08_metadata_spec.toon
Format: <TYPE>-<DOMAIN>-<UUID>
"""

import uuid
from enum import Enum


def make_id(prefix: str | Enum, domain: str = "GEN") -> str:
    if isinstance(prefix, Enum):
        prefix = prefix.value
    uid = uuid.uuid4().hex[:12].upper()
    return f"{prefix}-{domain}-{uid}"


def make_ekr_id(domain: str = "GEN") -> str:
    return make_id("EKR", domain)


def make_ka_id(domain: str = "GEN") -> str:
    return make_id("KA", domain)


def parse_id(identifier: str) -> dict:
    parts = identifier.split("-", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid identifier: {identifier}")
    return {"prefix": parts[0], "domain": parts[1], "uuid": parts[2]}
