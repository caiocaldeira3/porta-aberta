import os
import time
import dotenv
import asyncio
import fileinput
import regex as re
import dataclasses as dc

from pathlib import Path
from enum import auto, Enum
from werkzeug.security import generate_password_hash
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from sqlalchemy.exc import NoResultFound
from socketio.exceptions import ConnectionError

base_path = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(base_path / ".env", override=True)

import app.util.crypto as crypto
import app.util.jobs as jobs

from app.models.user import User
from app.models.chat import Chat

from app import db
from app import sio
from app import job_queue

class ConnectionResults (Enum):
    SUCESSFUL   = auto()
    RETRY       = auto()
    FAILED      = auto()

@dc.dataclass()
class Api:

    base_url: str = dc.field(init=False, default="http://127.0.0.1:5000")
    headers_client: dict = dc.field(init=False, default=None)
    headers_user: dict = dc.field(init=False, default=None)

    user_id: int = dc.field(init=False, default=None)
    id_key: X25519PrivateKey = dc.field(init=False, default=None)
    sgn_key: X25519PrivateKey = dc.field(init=False, default=None)
    ed_key: Ed25519PrivateKey = dc.field(init=False, default=None)

    def __init__ (self, logged_in: bool = False) -> None:
        self.headers_client = {
            "Param-Auth": os.environ["CHAT_SECRET"]
        }
        self.headers_user = self.headers_client

        if logged_in and os.environ["USER_ID"] != -1:
            self.login()

        elif logged_in:
            print("Api has not any session stored")
            raise Exception

    def _setup_user (self) -> None:
        self.user_id = os.environ["USER_ID"]
        self.id_key = crypto.load_private_key("id_key")
        self.sgn_key = crypto.load_private_key("sgn_key")
        self.ed_key = crypto.load_private_key("ed_key")

        self._update_header_user()

    def _setdown_user (self) -> None:
        self.user_id = None
        self.id_key = None
        self.sgn_key = None
        self.ed_key = None

        self._update_header_user(logout=True)

    def _update_enviroment (self, key: str, value: str) -> None:
        environ_regex = re.compile(f"(?<={key}=).*")
        os.environ[key] = str(value)

        with fileinput.FileInput(".env", inplace=True, backup=".bak") as env:
            for line in env:
                print(environ_regex.sub(f"{value}", line), end="")

    def _update_header_user (self, logout: bool = False) -> None:
        if logout:
            self.headers_user.pop("Signed-Message", None)

        else:
            self.headers_user = {
                "Signed-Message": crypto.sign_message(self.ed_key)
            } | self.headers_client

    def sign_message (self) -> str:
        return crypto.sign_message(self.ed_key)

    def logout (self) -> None:
        self._setdown_user()

        try:
            sio.disconnect()

        except:
            pass

    def login (self) -> ConnectionResults:
        try:
            self._setup_user()
            user = User.query.filter_by(id=self.user_id).one()

            sio.connect(
                self.base_url,
                auth={ "telephone": user.telephone },
                headers=self.headers_user
            )

            return ConnectionResults.SUCESSFUL

        except ConnectionError as exc:
            self._setdown_user()

            return ConnectionResults.FAILED

        except NoResultFound as exc:
            print("User not found on client database")

            self._setdown_user()
            return ConnectionResults.FAILED

        except Exception as exc:
            print(exc)

            self._setdown_user()
            return ConnectionResults.FAILED

    def signup (self, name: str, telephone: str, password: str) -> ConnectionResults:
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
            user = User(
                name=name,
                telephone=telephone,
                password=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()

            self.user_id = user.id

            sio.connect(
                self.base_url,
                auth={
                    "name": name,
                    "telephone": telephone,
                    "id_key": id_key,
                    "sgn_key": sgn_key,
                    "ed_key": ed_key,
                    "opkeys": opkeys
                }, headers=self.headers_client
            )

            self._update_header_user()
            self._update_enviroment("USER_ID", self.user_id)

            return ConnectionResults.SUCESSFUL

        except ConnectionError as exc:
            User.query.filter_by(id=user.id).delete()
            db.session.commit()

            self._setdown_user()
            raise exc
            return ConnectionResults.FAILED

    def create_chat (
        self, name: str, users: list[str], description: str = None
    ) -> ConnectionResults:
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

            data = {
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
            }
            sio.emit("create-chat", data=data)

            return ConnectionResults.SUCESSFUL

        except ConnectionRefusedError:
            print("Retry creating the chatroom")
            job_queue.add_job(self.user_id, 1, jobs.CreateChatJob, data=data, chat_id=chat.id)

            return ConnectionResults.RETRY

        except Exception as exc:
            return ConnectionResults.FAILED

    def send_message (self, chat_id: int, msg: str) -> ConnectionResults:
        try:
            owner = User.query.filter_by(id=self.user_id).one()
            chat = Chat.query.filter_by(id=chat_id).one()

            ratchets, pbkey = crypto.load_ratchets(chat_id)
            bmsg = bytes(msg, encoding="utf-8")
            cipher, new_ratchet_pbkey = crypto.snd_msg(
                ratchets, pbkey, bmsg
            )

            data = {
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
            }
            sio.send(data)

            ratchets.pop("snd_ratchet", None)
            ratchets.pop("user_ratchet", None)
            for ratchet_name, ratchet in ratchets.items():
                crypto.save_ratchet(chat_id, ratchet_name, ratchet, tmp=True)

            return ConnectionResults.SUCESSFUL

        except ConnectionRefusedError:
            job_queue.add_job(self.user_id, 2, jobs.SendMessageJob, data, chat.id)

            return ConnectionResults.RETRY

        except NoResultFound:
            return ConnectionResults.FAILED

        except Exception as exc:
            print(exc)

            return ConnectionResults.FAILED

    async def _job_handler (self) -> None:
        while True:
            if self.user_id != -1:
                job_queue.resolve_jobs(self.user_id)
                time.sleep(5)

    def job_handler (self) -> None:
        asyncio.run(self._job_handler())

