from pathlib import Path
from cryptography.fernet import Fernet


KEY_FILE = Path.home() / ".config" / "doc-rebuild" / ".key"


def _get_or_create_key(key_file: Path | None = None) -> bytes:
    kf = key_file or KEY_FILE
    if kf.exists():
        return kf.read_bytes()
    key = Fernet.generate_key()
    kf.parent.mkdir(parents=True, exist_ok=True)
    kf.write_bytes(key)
    kf.chmod(0o600)
    return key


def encrypt_token(token: str, key_file: Path | None = None) -> bytes:
    key = _get_or_create_key(key_file)
    f = Fernet(key)
    return f.encrypt(token.encode())


def decrypt_token(encrypted: bytes, key_file: Path | None = None) -> str:
    key = _get_or_create_key(key_file)
    f = Fernet(key)
    return f.decrypt(encrypted).decode()
