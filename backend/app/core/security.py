import secrets

from passlib.context import CryptContext

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

API_KEY_PREFIX = "rgs_"


def generate_api_key_raw() -> str:
    token = secrets.token_urlsafe(32)
    return f"{API_KEY_PREFIX}{token}"


def api_key_lookup_prefix(full_key: str, length: int = 8) -> str:
    """Return a short prefix from the secret portion (after rgs_) for indexed lookup."""
    body = full_key[len(API_KEY_PREFIX) :] if full_key.startswith(API_KEY_PREFIX) else full_key
    return body[:length] if len(body) >= length else body


def hash_api_key(raw_key: str) -> str:
    return _pwd.hash(raw_key)


def verify_api_key(raw_key: str, key_hash: str) -> bool:
    return _pwd.verify(raw_key, key_hash)
