"""Conservative direct-identifier masking for local prototype inputs.

The rules deliberately favor masking over preservation. They cover common
direct identifiers that can be recognized reliably without an external model.
They do not claim to detect every personal name, free-form address, or indirect
identifier; research datasets still require manual privacy review.
"""

from __future__ import annotations

import re


_EMAIL = re.compile(
    r"(?<![\w.+-])[\w.!#$%&'*+/=?^`{|}~-]+@(?:[\w-]+\.)+[A-Za-z]{2,63}(?![\w-])",
    re.IGNORECASE,
)
_URL = re.compile(r"\b(?:https?://|www\.)[^\s<>()]+", re.IGNORECASE)
_IPV4 = re.compile(
    r"(?<!\d)(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|1?\d?\d)(?!\d)"
)
_COORDINATES = re.compile(
    r"(?<!\w)[+-]?\d{1,2}\.\d{3,}\s*,\s*[+-]?\d{1,3}\.\d{3,}(?!\w)"
)
_DISCORD_TAG = re.compile(r"\b[A-Za-z0-9_.-]{2,32}#\d{4}\b")
_HANDLE = re.compile(r"(?<![\w@])@[A-Za-z0-9_][A-Za-z0-9_.-]{1,31}\b")
_PHONE_CANDIDATE = re.compile(r"(?<![\w.])\+?\d[\d\s().-]{5,}\d(?![\w.])")
_LONG_NUMERIC_ID = re.compile(r"(?<!\d)\d{12,22}(?!\d)")


def _redact_phone_candidate(match: re.Match[str]) -> str:
    value = match.group(0)
    return "[PHONE]" if sum(char.isdigit() for char in value) >= 7 else value


def redact_text(text: str) -> str:
    """Return *text* with common direct identifiers replaced by typed tokens."""

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    redacted = _EMAIL.sub("[EMAIL]", text)
    redacted = _URL.sub("[URL]", redacted)
    redacted = _IPV4.sub("[IP_ADDRESS]", redacted)
    redacted = _COORDINATES.sub("[COORDINATES]", redacted)
    redacted = _DISCORD_TAG.sub("[HANDLE]", redacted)
    redacted = _HANDLE.sub("[HANDLE]", redacted)
    redacted = _LONG_NUMERIC_ID.sub("[IDENTIFIER]", redacted)
    redacted = _PHONE_CANDIDATE.sub(_redact_phone_candidate, redacted)
    return redacted
