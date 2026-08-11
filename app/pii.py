from __future__ import annotations

import hashlib
import re
from re import Pattern

PII_PATTERNS: dict[str, Pattern[str]] = {
    "email": re.compile(r"[\w\.-]+@[\w\.-]+\.\w+"),
    "phone_vn": re.compile(r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)"),
    "cccd": re.compile(r"\b\d{12}\b"),
    "credit_card": re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),
    # TODO: Add more patterns (e.g., Passport, Vietnamese address keywords)
    "passport": re.compile(r"\b[A-Z]\d{7,8}\b", re.IGNORECASE),
    "address_vn": re.compile(
        r"\b(?:Số\s+\d+[^,\n]+|(?:ngõ|ngách|hẻm|đường|phố|phường|xã|thị trấn|quận|huyện|thị xã|tp\.?|thành phố|tỉnh)\s+[\w\s\d/]+(?:,\s*[\w\s\d/]+)*)",
        re.IGNORECASE,
    ),
}


def scrub_text(text: str) -> str:
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = pattern.sub(f"[REDACTED_{name.upper()}]", safe)
    return safe


def summarize_text(text: str, max_len: int = 80) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
