import os

from flask_socketio import emit, send

from app.models.user import User
from app.models.public_keys import OPKey

def create_chat (owner: User, user: User, opkeys: list[OPKey], data: dict) -> None:
    for device in user.devices:
        emit(
            "create-chat",
            {
                "status": "pending",
                "msg": f"Creating chat between {owner.telephone} and {user.telephone}",
                "data": {
                    "owner": {
                        "name": owner.name,
                        "telephone": owner.telephone,
                        "description": owner.description,
                        "chat_id": data["owner"]["chat_id"],
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
                }
            }, to=device.socket_id
        )

def send_message (receiver: User, data: dict) -> None:
    snd_tel = data["sender"]["telephone"]

    for device in receiver.devices:
        send({
            "status": "pending",
            "msg": f"Seding message from {snd_tel} to {receiver.telephone}",
            "data": data
        }, to=device.socket_id)