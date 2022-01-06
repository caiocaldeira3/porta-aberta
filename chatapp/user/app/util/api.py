import os
import json
import dotenv
import requests
import fileinput
import regex as re
import dataclasses as dc

from pathlib import Path
from werkzeug.security import generate_password_hash
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

base_path = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(base_path / ".env", override=True)

import app.util.crypto as crypto

from app.models.user import User
from app.models.chat import Chat

from app import db
from app import sio

@dc.dataclass()
class Api:

    base_url: str = dc.field(init=False, default="http://0.0.0.0:5000")
    headers_client: dict = dc.field(init=False, default=None)
    headers_user: dict = dc.field(init=False, default=None)

    user_id: int = dc.field(init=False, default=None)
    id_key: X25519PrivateKey = dc.field(init=False, default=None)
    sgn_key: X25519PrivateKey = dc.field(init=False, default=None)
    ed_key: Ed25519PrivateKey = dc.field(init=False, default=None)

    def __init__ (self, logged_in: str = None) -> None:
        self.headers_client = {
            "Param-Auth": os.environ["CHAT_SECRET"]
        }
        self.headers_user = self.headers_client

        if logged_in == "logged_in" and os.environ["USER_ID"] != -1:
            self.login()
            self.ping()

        elif logged_in == "logged_in":
            print("Api has not any session stored")
            raise Exception

    def login (self) -> None:
        self.user_id = os.environ["USER_ID"]
        self.id_key = crypto.load_private_key("id_key")
        self.sgn_key = crypto.load_private_key("sgn_key")
        self.ed_key = crypto.load_private_key("ed_key")

        self.update_header_user()

    def logout (self) -> None:
        self.user_id = None
        self.id_key = None
        self.sgn_key = None
        self.ed_key = None

        self.update_header_user(logout=True)

    def _update_enviroment (self, key: str, value: str) -> None:
        environ_regex = re.compile(f"(?<={key}=).*")
        os.environ[key] = str(value)

        with fileinput.FileInput(".env", inplace=True, backup=".bak") as env:
            for line in env:
                print(environ_regex.sub(f"{value}", line), end="")

    def update_header_user (self, logout: bool = False) -> None:
        if logout:
            self.headers_user.pop("Signed-Message", None)

        else:
            self.headers_user = {
                "Signed-Message": crypto.sign_message(self.ed_key)
            } | self.headers_client

    def ping (self) -> None:
        try:
            user = User.query.filter_by(id=self.user_id).one()
            sio.connect(
                self.base_url,
                auth={ "telephone": user.telephone },
                headers=self.headers_user
            )

        except Exception as exc:
            print(exc)

            self.logout()
            raise Exception

    def signup (
        self, name: str, telephone: str, password: str,
        description: str = None, email: str = None
    ) -> None:
        self.id_key = crypto.generate_private_key("id_key")
        self.sgn_key = crypto.generate_private_key("sgn_key")
        self.ed_key = crypto.generate_private_key("ed_key", sgn_key=True)

        id_key = crypto.public_key(self.id_key)
        sgn_key = crypto.public_key(self.sgn_key)
        ed_key = crypto.public_key(self.ed_key)
        opkeys = [
            { "id": idx, "key": crypto.public_key(crypto.generate_private_key(f"{idx}_opk")) }
            for idx in range(1, 11)
        ]

        try:
            sio.connect(
                self.base_url,
                auth={
                    key: value
                    for key, value in vars().items()
                    if key not in [ "self", "password" ] and value is not None
                }, headers=self.headers_client
            )

            user = User(
                name=name,
                telephone=telephone,
                password=generate_password_hash(password),
                email=email,
                description=description
            )
            db.session.add(user)
            db.session.commit()

            self.user_id = user.id
            self.update_header_user()
            self._update_enviroment("USER_ID", self.user_id)

        except Exception as exc:
            print(exc)
            User.query.filter_by(telephone=telephone).delete()
            db.session.commit()

            crypto.clean_keys()

            raise exc

    def sign_message (self) -> str:
        return crypto.sign_message(self.ed_key)

    def create_chat (
        self, name: str, users: list[str], description: str = None
    ) -> None:
        try:
            owner = User.query.filter_by(id=self.user_id).one()

            db_users = []
            for user in users:
                db_user = User.query.filter_by(telephone=user).first()
                if db_user is None:
                    db_user = User(telephone=user)

                    db.session.add(db_user)

                db_users.append(db_user)

            chat = Chat(
                name=name,
                users=db_users,
                description=description
            )
            db.session.add(chat)
            db.session.commit()

            eph_key = crypto.generate_private_key(f"eph-{chat.id}-{self.user_id}")
            dh_ratchet = crypto.generate_private_key(f"dhr-{chat.id}-{self.user_id}")

            sio.emit("create-chat", {
                "Signed-Message": self.sign_message(),
                "telephone": owner.telephone,
                "body": {
                    "owner": {
                        "telephone": owner.telephone,
                        "chat_id": chat.id
                    },
                    "name": name,
                    "users": users,
                    "dh_ratchet": crypto.public_key(dh_ratchet),
                    "EK": crypto.public_key(eph_key)
                },
            })

        except Exception as exc:
            Chat.query.filter_by(id=chat.id).delete()
            db.session.commit()

            raise exc

    def send_message (self, chat_id: int, msg: str) -> None:
        try:
            owner = User.query.filter_by(id=self.user_id).one()
            chat = Chat.query.filter_by(id=chat_id).one()

            ratchets, pbkey = crypto.load_ratchets(chat_id)
            bmsg = bytes(msg, encoding="utf-8")
            cipher, new_ratchet_pbkey = crypto.snd_msg(
                ratchets, pbkey, bmsg
            )

            sio.send({
                "Signed-Message": self.sign_message(),
                "telephone": owner.telephone,
                "body": {
                    "sender": {
                        "telephone": owner.telephone,
                        "chat_id": chat.id
                    },
                    "receiver": {
                        "telephone": chat.users[0].telephone,
                        "chat_id": chat.chat_id
                    },
                    "cipher": crypto.decode_b64(cipher),
                    "dh_ratchet": new_ratchet_pbkey
                }
            })

            ratchets.pop("snd_ratchet", None)
            ratchets.pop("user_ratchet", None)
            for ratchet_name, ratchet in ratchets.items():
                crypto.save_ratchet(chat_id, ratchet_name, ratchet, tmp=True)

        except Exception as exc:
            print(exc)

            raise exc