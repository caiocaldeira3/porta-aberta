import os
import shutil
import dotenv
import base64

from typing import Union
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from pathlib import Path

base_path = Path(__file__).resolve().parent.parent.parent
ratchets_path = base_path / "app/util/ratchets"
keys_path = base_path / "app/util/encrypted_keys"

dotenv.load_dotenv(base_path / ".env", override=False)

ratchets_iter = [
    ("dh_ratchet", "private"), ("root_ratchet", "symmetric"), ("user_ratchet", "public")
]

class SymmetricRatchet(object):
    def __init__ (self, key: bytes):
        self.state = key

    def next (self, inp: bytes = b"", init_vector: bytes = b"") -> bytes:
        output = hkdf_derive_key(self.state + inp, 80)
        self.state = output[ : 32 ]

        # key, initializing vector
        return output[ 32 : 64 ], output[ 64: ]

PrivateKey = Union[Ed25519PrivateKey, X25519PrivateKey]
PublicKey = Union[Ed25519PublicKey, X25519PublicKey]
Ratchet = Union[ SymmetricRatchet, PrivateKey ]
Key = Union[PrivateKey, PublicKey, SymmetricRatchet]

def ensure_dir (file_path: str) -> None:
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def decode_b64 (msg: bytes) -> str:
    return base64.encodebytes(msg).decode("utf-8").strip()

def encode_b64 (msg: str) -> bytes:
    return base64.b64decode(msg)

def pad (msg: bytes) -> bytes:
    # pkcs7 padding
    num = 16 - (len(msg) % 16)
    return msg + bytes([num] * num)

def unpad (msg: bytes) -> bytes:
    # remove pkcs7 padding
    return msg[ : -msg[-1] ]

def hkdf_derive_key (input: bytes, length: int) -> bytes:
    hkdf_key = HKDF(
        algorithm=hashes.SHA256(), length=length, salt=b"", info=b"", backend=default_backend()
    )

    return hkdf_key.derive(input)

def sender_x3dh (
    sender_keys: dict[str, PrivateKey], recv_keys: dict[str, PublicKey]
) -> bytes:
    dh1 = sender_keys["IK"].exchange(recv_keys["SPK"])
    dh2 = sender_keys["EK"].exchange(recv_keys["IK"])
    dh3 = sender_keys["EK"].exchange(recv_keys["SPK"])
    dh4 = sender_keys["EK"].exchange(recv_keys["OPK"])

    return hkdf_derive_key(dh1 + dh2 + dh3 + dh4, 32)

def receiver_x3dh (
    sender_keys: dict[str, PublicKey], recv_keys: dict[str, PrivateKey]
) -> bytes:
    dh1 = recv_keys["SPK"].exchange(sender_keys["IK"])
    dh2 = recv_keys["IK"].exchange(sender_keys["EK"])
    dh3 = recv_keys["SPK"].exchange(sender_keys["EK"])
    dh4 = recv_keys["OPK"].exchange(sender_keys["EK"])

    return hkdf_derive_key(dh1 + dh2 + dh3 + dh4, 32)

def init_root_ratchet (shared_key: bytes) -> SymmetricRatchet:
    return SymmetricRatchet(shared_key)

def dh_ratchet_rotation_receive (
    ratchets: dict[str, Ratchet], pbkey: bytes
) -> None:
    dh_recv = ratchets["dh_ratchet"].exchange(pbkey)
    shared_recv = ratchets["root_ratchet"].next(dh_recv)[0]

    ratchets["rcv_ratchet"] = SymmetricRatchet(shared_recv)

def dh_ratchet_rotation_send (
    ratchets: dict[str, Ratchet], pbkey: PublicKey
) -> None:
    ratchets["dh_ratchet"] = X25519PrivateKey.generate()
    dh_send = ratchets["dh_ratchet"].exchange(pbkey)
    shared_send = ratchets["root_ratchet"].next(dh_send)[0]

    ratchets["snd_ratchet"] = SymmetricRatchet(shared_send)

def create_chat_encryption (
    pvt_keys: dict[str, PrivateKey], pb_keys: dict[str, PublicKey], sender: bool
) -> SymmetricRatchet:
    pb_keys = {
        key: X25519PublicKey.from_public_bytes(encode_b64(value))
        for key, value in pb_keys.items()
    }

    if sender:
        shared_key = sender_x3dh(sender_keys=pvt_keys, recv_keys=pb_keys)
    else:
        shared_key = receiver_x3dh(sender_keys=pb_keys, recv_keys=pvt_keys)

    return init_root_ratchet(shared_key)

def snd_msg (
    ratchets: dict[str, Ratchet], pbkey: PublicKey, msg: bytes
) -> tuple[bytes, PublicKey]:
    dh_ratchet_rotation_send(ratchets, pbkey)
    key, init_vector = ratchets["snd_ratchet"].next()
    cipher = Cipher(algorithms.AES(key), modes.CBC(init_vector))
    encryptor = cipher.encryptor()
    enc_msg = encryptor.update(pad(msg)) + encryptor.finalize()

    return enc_msg, public_key(ratchets["dh_ratchet"])

def rcv_msg (
    ratchets: dict[str, Ratchet], pbkey: bytes, enc_msg: bytes
) -> bytes:
    dh_ratchet_rotation_receive(ratchets, pbkey)
    key, init_vector = ratchets["rcv_ratchet"].next()
    cipher = Cipher(algorithms.AES(key), modes.CBC(init_vector))
    decryptor = cipher.decryptor()

    return unpad(decryptor.update(enc_msg) + decryptor.finalize())

def generate_private_key (name: str = None, sgn_key: bool = False) -> PrivateKey:
    pvt_key = X25519PrivateKey.generate() if not sgn_key else Ed25519PrivateKey.generate()
    if name is not None:
        save_private_key(name, pvt_key)

    return pvt_key

def save_private_key (name: str, pvtkey: PrivateKey) -> None:
    with open(keys_path / f"{name}.pem", "w") as pem_file:
        encoded_pvtkey = pvtkey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(
                encode_b64(os.environ["SECRET_KEY"])
            )
        )

        pem_file.write(f"{decode_b64(encoded_pvtkey)}")

def save_ratchet (chat_id: int, ratchet_name: str, ratchet: Union[Ratchet, str]) -> None:
    ensure_dir(ratchets_path / f"{chat_id}/{ratchet_name}" )
    if isinstance(ratchet, X25519PrivateKey):
        with open(ratchets_path / f"{chat_id}/{ratchet_name}.pem", "w") as pem_file:
            encoded_ratchet = ratchet.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(
                    encode_b64(os.environ["SECRET_KEY"])
                )
            )

            pem_file.write(f"{decode_b64(encoded_ratchet)}")

    elif isinstance(ratchet, SymmetricRatchet):
        with open(ratchets_path / f"{chat_id}/{ratchet_name}", "w") as sym_file:
            sym_file.write(f"{decode_b64(ratchet.state)}")

    elif isinstance(ratchet, str):
        with open(ratchets_path / f"{chat_id}/{ratchet_name}", "w") as pbk_file:
            pbk_file.write(f"{ratchet}")

def load_key_from_file (
    key_path: Path, key_name: str, method: str = "private", **kwargs
) -> Key:
    if method == "private":
        with open(key_path / f"{key_name}.pem") as pem_file:
            return serialization.load_pem_private_key(
                backend=default_backend(),
                password=encode_b64(os.environ["SECRET_KEY"]),
                data=encode_b64("\n".join(pem_file.readlines()))
            )
    elif method == "symmetric":
        with open(key_path / f"{key_name}") as sym_file:
            return SymmetricRatchet(encode_b64(sym_file.readline()))

    elif method == "public":
        with open(key_path / f"{key_name}") as sym_file:
            return load_public_key(sym_file.readline(), **kwargs)

def load_ratchets (chat_id: int) -> tuple[dict[str, Ratchet], bytes]:
    ratchets = dict()
    for ratchet_name, ratchet_method in ratchets_iter:
        ratchets[ratchet_name] = load_key_from_file(
            ratchets_path / f"{chat_id}",
            ratchet_name,
            ratchet_method
        )

    pbkey = ratchets.pop("user_ratchet")

    return ratchets, pbkey

def public_key (key: Union[PrivateKey, PublicKey]) -> str:
    if isinstance(key, X25519PrivateKey):
        key = key.public_key()

    if isinstance(key, Ed25519PrivateKey):
        key = key.public_key()

    return decode_b64(
        key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    )

def load_public_key (pbkey: str, sgn_key: bool = False) -> PublicKey:
    if sgn_key:
        return Ed25519PublicKey.from_public_bytes(encode_b64(pbkey))
    else:
        return X25519PublicKey.from_public_bytes(encode_b64(pbkey))

def sign_message (pvtkey: Ed25519PrivateKey) -> str:
    return decode_b64(
        pvtkey.sign(b"It's me, Mario")
    ).replace("\r", "").replace("\n", "")

def load_private_key (name: str) -> PrivateKey:
    return load_key_from_file(keys_path, name)

def clean_keys () -> None:
    for item in os.listdir(keys_path):
        if item.endswith(".pem"):
            os.remove(keys_path / item)
    shutil.rmtree(ratchets_path, ignore_errors=True)

def clean_chat_keys (chat_id: int, user_id: int) -> None:
    for item in os.listdir(keys_path):
        if item.endswith(f"{chat_id}-{user_id}.pem"):
            os.remove(keys_path / item)