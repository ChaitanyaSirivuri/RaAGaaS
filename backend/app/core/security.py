import secrets

from passlib.context import CryptContext

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

API_KEY_PREFIX = "rgs_"


def generate_api_key_raw() -> str:
    token = secrets.token_urlsafe(32)
    return f"{API_KEY_PREFIX}{token}"


def api_key_prefix_display(full_key: str, length: int = 8) -> str:
    return full_key[:length] if len(full_key) >= length else full_key


def hash_api_key(raw_key: str) -> str:
    return _pwd.hash(raw_key)


def verify_api_key(raw_key: str, key_hash: str) -> bool:
    return _pwd.verify(raw_key, key_hash)
