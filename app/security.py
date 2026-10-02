import secrets
import string
import re

ALPHABET = string.ascii_letters + string.digits

def generate_code(length: int = 7) -> str:
    return ''.join(secrets.choice(ALPHABET) for _ in range(length))

def validate_alias(alias: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_-]{3,32}", alias))
