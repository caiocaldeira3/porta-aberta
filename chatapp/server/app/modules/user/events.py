from typing import Union
from flask_socketio import ConnectionRefusedError, emit

# Import Util Modules
from app.util import api
from app.util.jobs import ConfirmCreateChatJob, ConfirmMessageJob
from app.util.authentication import authenticate_source, authenticate_user

# Import module models (i.e. Organization)
from app.models.user import User

from app import sio
from app import job_queue

RequestData = Union[str, dict[str, str]]

@sio.on("create-chat")
@authenticate_source()
@authenticate_user()
def handle_create_chat (sid: str, data: dict[str, RequestData]) -> None:
    try:
        owner = User.query.filter_by(telephone=data["owner"]["telephone"]).one()
        users = User.query.filter(User.telephone.in_(data["users"])).all()

        data.pop("users", None)
        for user in users:
            opkeys = user.opkeys[ : 2 ]
            api.create_chat(owner, user, opkeys, data)

    except Exception as exc:
        print(exc)

        raise ConnectionRefusedError

@sio.on("confirm-create-chat")
@authenticate_source()
@authenticate_user()
def handle_confirm_create_chat (sid: str, data: dict[str, RequestData]) -> None:
    try:
        owner = User.query.filter_by(telephone=data["owner"]["telephone"]).one()
        user_tel = data["user"]["telephone"]

        resp_data = {
            "status": "ok",
            "msg": f"Chat created between users {owner.telephone} and {user_tel}",
            "data": data
        }

        if len(owner.devices) == 0:
            job_queue.add_job(owner.id, 2, ConfirmCreateChatJob, resp_data)

            return

        for device in owner.devices:
            try:
                emit("confirm-create-chat", resp_data, to=device.socket_id)

            except ConnectionRefusedError:
                job_queue.add_job(owner.id, 2, ConfirmCreateChatJob, resp_data)


    except Exception as exc:
        print(exc)

        raise ConnectionRefusedError

@sio.on("message")
@authenticate_source()
@authenticate_user()
def handle_message (sid: str, data: dict[str, RequestData]) -> None:
    try:
        user = User.query.filter_by(telephone=data["receiver"]["telephone"]).one()
        api.send_message(user, data)

    except Exception as exc:
        print(exc)

        raise ConnectionRefusedError

@sio.on("confirm-message")
@authenticate_source()
@authenticate_user()
def handle_confirm_message (sid: str, data: dict[str, RequestData]) -> None:
    try:
        sender = User.query.filter_by(telephone=data["sender"]["telephone"]).one()
        rcv_tel = data["receiver"]["telephone"]

        resp_data = {
            "status": "ok",
            "msg": f"Message sent from {sender.telephone} to {rcv_tel}",
            "data": data
        }

        if len(sender.devices) == 0:
            print("Queueing confirm message due to lack of devices")
            job_queue.add_job(sender.id, 2, ConfirmMessageJob, resp_data)

            return

        for device in sender.devices:
            try:
                emit("confirm-message", resp_data, to=device.socket_id)

            except ConnectionRefusedError:
                job_queue.add_job(sender.id, 2, ConfirmMessageJob, resp_data)

    except Exception as exc:
        print(exc)

        raise ConnectionRefusedError