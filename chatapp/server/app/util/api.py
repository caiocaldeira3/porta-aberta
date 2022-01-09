from flask_socketio import emit, send

from app.models.user import User
from app.models.public_keys import OPKey

from app.util.jobs import CreateChatJob, SendMessageJob

from app import sio
from app import job_queue

def create_chat (owner: User, user: User, opkeys: list[OPKey], req_info: dict) -> None:
    data = {
        "status": "pending",
        "msg": f"Creating chat between {owner.telephone} and {user.telephone}",
        "data": {
            "owner": {
                "name": owner.name,
                "telephone": owner.telephone,
                "description": owner.description,
                "chat_id": req_info["owner"]["chat_id"],
                "keys": {
                    "pb_keys": {
                        "IK": owner.id_key,
                        "EK": req_info["EK"],
                    }
                },
            },
            "user": {
                "telephone": user.telephone,
                "used_keys": [ opkeys[0].key_id, opkeys[1].key_id ],
                "dh_ratchet": req_info["dh_ratchet"]
            },
            "name": req_info["name"],
        }
    }

    if len(user.devices) == 0:
        job_queue.add_job(user.id, 1, CreateChatJob, data)
        return

    for device in user.devices:
        try:
            emit("create-chat", data, to=device.socket_id)

        except ConnectionRefusedError as exc:
            print(f"Queueing chat creation between {owner.telephone} and {user.telephone}")
            job_queue.add_job(user.id, 1, CreateChatJob, data)

        except Exception as exc:
            print(exc)

            raise Exception

def send_message (receiver: User, req_info: dict) -> None:
    snd_tel = req_info["sender"]["telephone"]
    data = {
        "status": "pending",
        "msg": f"Sending message from {snd_tel} to {receiver.telephone}",
        "data": req_info
    }

    if len(receiver.devices) == 0:
        job_queue.add_job(receiver.id, 2, SendMessageJob, data)
        return

    for device in receiver.devices:
        try:
            send(data, to=device.socket_id)

        except ConnectionRefusedError as exc:
            print(f"Queueing send messsage to {receiver.telephone}")
            job_queue.add_job(receiver.id, 2, SendMessageJob, data)

        except Exception as exc:
            print(exc)

            raise Exception