import os
import threading

from typing import Callable
from functools import wraps

from flask import request, wrappers
from flask_socketio import emit, ConnectionRefusedError

from app.models.user import User
from app.models.device import Device
from app.models.public_keys import OPKey

from app.util.jobs import AddUserDeviceJob
from app.util.crypto import verify_signed_message

from app import db
from app import job_queue

def authenticate_source () -> wrappers.Response:
    def wrapper (f: Callable) -> wrappers.Response:
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.headers["Param-Auth"] == os.environ["CHAT_SECRET"]:
                return f(request.sid, *args, **kwargs)

            else:
                emit("auth_response", {
                    "status": "failed",
                    "msg": "Unable to authenticate connection source"
                })

                raise ConnectionRefusedError

        return decorated

    return wrapper

def ensure_user () -> wrappers.Response:
    def wrapper (f: Callable) -> wrappers.Response:
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.headers.get("Signed-Message", None) is not None:
                try:
                    sid, data = args
                    user = User.query.filter_by(telephone=data["telephone"]).one()
                    sgn_message = request.headers["Signed-Message"]
                    verify_signed_message(user, sgn_message)

                    job_queue.add_job(-1, 0, AddUserDeviceJob, {"user_id": user.id, "sid": sid})

                    return f(*args, "ok", **kwargs)

                except Exception as exc:
                    print(exc)
                    emit("auth_response", {
                        "status": "failed",
                        "msg": "Unable to authenticate signed message"
                    })

                    raise ConnectionRefusedError

            else:
                try:
                    sid, auth_data = args

                    user = User(
                        name=auth_data["name"],
                        id_key=auth_data["id_key"],
                        sgn_key=auth_data["sgn_key"],
                        ed_key=auth_data["ed_key"],
                        devices=[ Device(socket_id=sid) ],
                        opkeys=[
                            OPKey(key_id=opkey["id"], opkey=opkey["key"])
                            for opkey in auth_data["opkeys"]
                        ],
                        telephone=auth_data.get("telephone"),
                        email=auth_data.get("email", None),
                        description=auth_data.get("description", None)
                    )

                    db.session.add(user)
                    db.session.add_all(user.devices)
                    db.session.add_all(user.opkeys)
                    db.session.commit()

                    return f(sid, {
                        "telephone": user.telephone
                    }, "created", **kwargs)

                except Exception as exc:
                    print(exc)
                    emit("auth_response", {
                        "status": "failed",
                        "msg": "Unable to create a new user"
                    })

                    raise ConnectionRefusedError

        return decorated

    return wrapper

def authenticate_user () -> wrappers.Response:
    def wrapper (f: Callable) -> wrappers.Response:
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                sid, data = args
                sgn_message = data.pop("Signed-Message")
                user = User.query.filter_by(telephone=data.pop("telephone")).one()

                data = data.pop("body")
                verify_signed_message(user, sgn_message)

                return f(sid, data, **kwargs)

            except Exception as exc:
                print(exc)
                emit("auth_response", {
                    "status": "failed",
                    "msg": "Unable to authenticate signed message"
                })

                raise ConnectionRefusedError

        return decorated

    return wrapper
