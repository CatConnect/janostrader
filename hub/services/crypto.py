import base64
import json
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from config import settings


def _key() -> bytes:
    """Deriva 32 bytes da ENCRYPTION_KEY via base64 ou raw."""
    k = settings.ENCRYPTION_KEY.encode()
    # Pad/truncate para 32 bytes
    return (k * 4)[:32]


def encrypt(data: dict) -> str:
    """Encripta um dicionÃ¡rio como JSON e retorna string base64."""
    key = _key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    plaintext = json.dumps(data).encode()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    combined = nonce + ciphertext
    return base64.b64encode(combined).decode()


def decrypt(token: str) -> dict:
    """Descriptografa e retorna o dicionÃ¡rio original."""
    key = _key()
    aesgcm = AESGCM(key)
    combined = base64.b64decode(token.encode())
    nonce = combined[:12]
    ciphertext = combined[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode())

