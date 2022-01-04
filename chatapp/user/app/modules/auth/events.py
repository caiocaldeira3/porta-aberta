from app.models.user import User

from app import db
from app import api
from app import sio


@sio.on("connect")
def handle_connect () -> None:
    print(f"connection established")

@sio.on("auth_response")
def handle_auth_response (auth_data: dict):
    if auth_data["status"] == "ok":
        pass

    else:
        api.logout()

        if auth_data.get(["body"], None) is not None:
            telephone = auth_data["body"]["telephone"]

            User.query.filter_by(telephone=telephone).delete()
            db.session.commit()

@sio.event
def disconnect ():
    api.logout()
    print("disconnected from server")