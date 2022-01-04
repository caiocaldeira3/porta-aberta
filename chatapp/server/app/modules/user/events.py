from typing import Union
from flask_socketio import ConnectionRefusedError, emit

# Import Util Modules
from app.util import api
from app.util.authentication import authenticate_source, authenticate_user

# Import module models (i.e. Organization)
from app.models.user import User

from app import sio

RequestData = Union[str, dict[str, str]]

@sio.on("create-chat")
@authenticate_source()
@authenticate_user()
def handle_create_chat (sid: str, data: dict[str, RequestData]) -> None:
    try:
        owner = User.query.filter_by(telephone=data["telephone"]).one()
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
        owner = User.query.filter_by(telephone=data.pop("owner")).one()
        for device in owner.devices:
            emit("confirm-create-chat", data, to=device.socket_id)

    except Exception as exc:
        print(exc)

        raise ConnectionRefusedError

@sio.on("message")
@authenticate_source()
@authenticate_user()
def handle_message (sid: str, data: dict[str, RequestData]) -> None:
    try:
        users = User.query.filter(User.telephone.in_(data["users"])).all()
        if len(users) == 0:
            raise Exception

        data["owner"] = data.pop("telephone", None)
        data.pop("users", None)

        for user in users:
            api.send_message(user, data)

    except Exception as exc:
        print(exc)

        raise ConnectionRefusedError

@sio.on("confirm-message")
@authenticate_source()
@authenticate_user()
def handle_confirm_message (sid: str, data: dict[str, RequestData]) -> None:
    try:
        owner = User.query.filter_by(telephone=data["owner"]).one()
        for device in owner.devices:
            emit("confirm-message", data, to=device.socket_id)

    except Exception as exc:
        print(exc)

        raise ConnectionRefusedError