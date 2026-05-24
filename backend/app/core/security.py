from __future__ import annotations

PROMPT_INJECTION_PHRASES = [
    "ignore previous instructions",
    "reveal system prompt",
    "exfiltrate",
    "developer message",
    "jailbreak",
]


def mask_pii(text: str) -> str:
    masked_tokens: list[str] = []
    for token in text.split():
        clean = token.strip(".,;:!?'\"()[]{}")
        if _looks_like_email(clean):
            masked_tokens.append(token.replace(clean, "[REDACTED_EMAIL]"))
            continue
        if _looks_like_phone(clean):
            masked_tokens.append(token.replace(clean, "[REDACTED_PHONE]"))
            continue
        masked_tokens.append(token)
    return " ".join(masked_tokens)


def has_prompt_injection_signal(text: str) -> bool:
    normalized = " ".join(text.lower().split())
    return any(phrase in normalized for phrase in PROMPT_INJECTION_PHRASES)


def _looks_like_email(token: str) -> bool:
    if token.count("@") != 1:
        return False
    local, domain = token.split("@")
    return bool(local and domain and "." in domain and not domain.startswith(".") and not domain.endswith("."))


def _looks_like_phone(token: str) -> bool:
    allowed = set("0123456789+-() ")
    if any(char not in allowed for char in token):
        return False
    digits = sum(1 for char in token if char.isdigit())
    return digits >= 8
