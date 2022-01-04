import os

from flask_socketio import emit, send

from app import db, sio
from app.models.user import User
from app.models.public_keys import OPKey

headers_server = {
    "Param-Auth": os.environ["SECRET_KEY"]
}

def create_chat (owner: User, user: User, opkeys: list[OPKey], data: dict) -> None:
    for device in user.devices:
        emit(
            "create-chat",
            {
                "owner": {
                    "name": owner.name,
                    "telephone": owner.telephone,
                    "description": owner.description,
                    "chat_id": data["chat_id"],
                    "keys": {
                        "pb_keys": {
                            "IK": owner.id_key,
                            "EK": data["EK"],
                        }
                    },
                },
                "user": {
                    "telephone": user.telephone,
                    "used_keys": [ opkeys[0].key_id, opkeys[1].key_id ],
                    "dh_ratchet": data["dh_ratchet"]
                },
                "name": data["name"],
            }, to=device.socket_id
        )

def send_message (user: User, data: dict) -> None:
    data = data | {"user": user.telephone}
    for device in user.devices:
        send(data, to=device.socket_id)