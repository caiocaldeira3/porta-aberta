from typing import Union

from app.models.user import User

from app import db
from app import api
from app import sio

ResponseData = dict[str, Union[str, dict[str, str]]]

@sio.on("connect")
def handle_connect () -> None:
    print(f"connection established")

@sio.on("auth_response")
def handle_auth_response (resp: dict):
    print(resp["msg"])
    if resp["status"] == "ok":
        pass

    else:
        api.logout()

        if resp.get(["data"], None) is not None:
            telephone = resp["data"]["telephone"]

            User.query.filter_by(telephone=telephone).delete()
            db.session.commit()

@sio.event
def disconnect ():
    api.logout()
    print("disconnected from server")