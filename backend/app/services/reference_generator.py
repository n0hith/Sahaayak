"""Deterministic, collision-resistant readiness-reference generation.

Replaces the frontend's `Math.random()`-based `SHY-2026-#####` (see
src/components/Handoff.tsx) with a hash derived from stable inputs
(session id, scheme id, timestamp, attempt number). Collisions are still
checked and retried against the DB by the caller (routers/handoff.py) -
this function alone does not guarantee uniqueness, it only makes
uniqueness overwhelmingly likely and reproducible for a given input.
"""

import base64
import hashlib
from datetime import datetime


def generate_reference_code(session_id: str, scheme_id: str, created_at: datetime, attempt: int = 0) -> str:
    year = created_at.year
    seed = f"{session_id}:{scheme_id}:{created_at.isoformat()}:{attempt}".encode("utf-8")
    digest = hashlib.sha256(seed).digest()
    # Base32 avoids ambiguous characters (0/O, 1/I) better than hex/base64,
    # which matters since this is meant to be read and typed by a person.
    encoded = base64.b32encode(digest).decode("ascii").rstrip("=")
    suffix = encoded[:5].upper()
    return f"SHY-{year}-{suffix}"
