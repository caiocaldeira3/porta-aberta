from flask import request
from flask_socketio import emit

from app.util.authentication import authenticate_source, ensure_user

from app.models.user import User
from app.models.device import Device

from app import db
from app import sio
from app import job_queue

@sio.on("connect")
@authenticate_source()
@ensure_user()
def handle_connect (sid: str, data: dict[str, str], status: str) -> None:
    user = User.query.filter_by(telephone=data["telephone"]).one()
    print(f"connect {sid}")
    emit("auth_response", {
        "status": status,
        "msg": "Session Authenticated",
        "data": {
            "user": {
                "id": user.id,
                "telephone": user.telephone
            }
        }
    })

@sio.on("disconnect")
def disconnect () -> None:
    Device.query.filter_by(socket_id=request.sid).delete()
    db.session.commit()

    job_queue.remove_jobs(sid=request.sid)
    print(f"disconnect {request.sid}")