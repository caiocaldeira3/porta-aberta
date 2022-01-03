import os
import sys
import json
import dotenv
import requests
import fileinput
import regex as re
import dataclasses as dc

from pathlib import Path
from sqlalchemy.orm import exc
from werkzeug.security import generate_password_hash
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

base_path = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(base_path / ".env", override=False)

import app.util.crypto as crypto

from app.models.user import User
from app.models.chat import Chat

from app import db
from app.util.json_encoder import ComplexEncoder

@dc.dataclass()
class Api:

    base_url: str = dc.field(init=False, default="http://0.0.0.0:8080")
    headers_client: dict = dc.field(init=False, default=None)
    headers_user: dict = dc.field(init=False, default=None)
    device_url: str = dc.field(init=False, default=None)

    user_id: int = dc.field(init=False, default=None)
    id_key: X25519PrivateKey = dc.field(init=False, default=None)
    sgn_key: X25519PrivateKey = dc.field(init=False, default=None)
    ed_key: Ed25519PrivateKey = dc.field(init=False, default=None)

    def __init__ (self, logged_in: str = None, port: str = None) -> None:
        self.device_url = f"http://0.0.0.0:{port if port is not None else 3030}"
        self.headers_client = {
            "Param-Auth": os.environ["CHAT_SECRET"]
        }

        if logged_in == "logged_in" and os.environ["USER_ID"] != -1:
            self.user_id = os.environ["USER_ID"]
            self.id_key = crypto.load_private_key("id_key")
            self.sgn_key = crypto.load_private_key("sgn_key")
            self.ed_key = crypto.load_private_key("ed_key")

            self.update_header_user()
            if not self.ping():
                raise Exception

        elif logged_in == "logged_in":
            print("Api has not any session stored")
            raise Exception

    def _update_enviroment (self, key: str, value: str) -> None:
        environ_regex = re.compile(f"(?<={key}=).*")

        with fileinput.FileInput(".env", inplace=True, backup=".bak") as env:
            for line in env:
                print(environ_regex.sub(f"{value}", line), end="")

    def update_header_user (self) -> None:
        self.headers_user = {
            "Signed-Message": crypto.sign_message(self.ed_key)
        } | self.headers_client

    def ping (self) -> bool:
        try:
            user = User.query.filter_by(id=self.user_id).one()
            response = requests.put(
                url=f"{self.base_url}/auth/ping/",
                json=json.dumps({
                    "telephone": user.telephone
                }),
                headers=self.headers_user
            )

            resp_json = response.json()
            if resp_json["status"] == "ok":
                return True

        except:
            return False

    def signup (
        self, name: str, telephone: str, password: str,
        description: str = None, email: str = None
    ) -> None:
        self.id_key = crypto.generate_private_key("id_key")
        self.sgn_key = crypto.generate_private_key("sgn_key")
        self.ed_key = crypto.generate_private_key("ed_key", sgn_key=True)

        address = self.device_url
        id_key = crypto.public_key(self.id_key)
        sgn_key = crypto.public_key(self.sgn_key)
        ed_key = crypto.public_key(self.ed_key)
        opkeys = [
            { "id": idx, "key": crypto.public_key(crypto.generate_private_key(f"{idx}_opk")) }
            for idx in range(1, 11)
        ]

        try:
            response = requests.post(
                url=f"{self.base_url}/auth/signup/",
                headers=self.headers_client,
                json=json.dumps({
                    key: value
                    for key, value in vars().items()
                    if key not in [ "self", "password" ] and value is not None
                }, cls=ComplexEncoder)
            )

            resp_json = response.json()
            if resp_json["status"] == "ok":
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

                return resp_json["data"]

        except Exception as exc:
            crypto.clean_keys()
            raise exc

    def create_chat (
        self, name: str, users: list[str], description: str = None
    ) -> None:
        try:
            owner = User.query.filter_by(id=self.user_id).one()
            last_chat = Chat.query.order_by(Chat.id.desc()).first()
            eph_key = crypto.generate_private_key()
            dh_ratchet = crypto.generate_private_key()

            response = requests.post(
                url=f"{self.base_url}/user/create-chat/",
                headers=self.headers_user,
                json=json.dumps({
                    "name": name,
                    "telephone": owner.telephone,
                    "chat_id": 1 if last_chat is None else last_chat.id + 1,
                    "users": users,
                    "dh_ratchet": crypto.public_key(dh_ratchet),
                    "EK": crypto.public_key(eph_key),
                })
            )

            resp_json = response.json()
            if resp_json["status"] == "ok":
                data = resp_json["data"][0]

                user = User.query.filter_by(telephone=data["telephone"]).first()
                if user is None:
                    user = User(name=data["name"], telephone=data["telephone"])

                    db.session.add(user)
                    db.session.commit()

                chat = Chat(
                    name = data["name"],
                    users = [ user ],
                    chat_id = data["chat_id"],
                    description = data.get("description", None)
                )
                db.session.add(chat)
                db.session.commit()

                user_ratchet = data["keys"].pop("dh_ratchet")
                user_keys = data["keys"]
                root_ratchet = crypto.create_chat_encryption(
                    { "IK": self.id_key, "EK": eph_key }, pb_keys=user_keys, sender=True
                )

                crypto.save_ratchet(chat.id, "dh_ratchet", dh_ratchet)
                crypto.save_ratchet(chat.id, "user_ratchet", user_ratchet)
                crypto.save_ratchet(chat.id, "root_ratchet", root_ratchet)

                return chat.id

        except Exception as exc:
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

            response = requests.post(
                url=f"{self.base_url}/user/send-message/",
                headers=self.headers_user,
                json=json.dumps({
                    "telephone": owner.telephone,
                    "users": [ chat.users[0].telephone ],
                    "chat_id": chat.chat_id,
                    "cipher": crypto.decode_b64(cipher),
                    "dh_ratchet": new_ratchet_pbkey
                })
            )

            resp_json = response.json()
            if resp_json["status"] == "ok":
                print(resp_json["msg"])

                ratchets.pop("snd_ratchet", None)
                ratchets["user_ratchet"] = resp_json["data"]["dh_ratchets"][0]
                for ratchet_name, ratchet in ratchets.items():
                    crypto.save_ratchet(chat_id, ratchet_name, ratchet)

        except Exception as exc:
            raise exc
            print("Message not delivered")