import base64

from typing import Union
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey

from app.models.user import User

def decode_b64 (msg: bytes) -> str:
    return base64.encodebytes(msg).decode("utf-8").strip()

def encode_b64 (msg: str) -> bytes:
    return base64.b64decode(msg)

PublicKeys = Union[Ed25519PublicKey, X25519PublicKey]

def load_public_key (pbkey: str, sgn_key: bool = False) -> PublicKeys:
    if sgn_key:
        return Ed25519PublicKey.from_public_bytes(encode_b64(pbkey))
    else:
        return X25519PublicKey.from_public_bytes(encode_b64(pbkey))

def verify_signed_message (user: User, msg: str) -> bool:
    ed_pbkey = load_public_key(user.ed_key, sgn_key=True)
    ed_pbkey.verify(signature=encode_b64(msg), data=b"It's me, Mario")
