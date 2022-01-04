from app.models.user import User
from app.models.user import Chat

from app.util import crypto

from app import db
from app import api
from app import sio

@sio.on("create-chat")
def create_chat (data):
    user = User.query.filter_by(id=api.user_id).one()
    owner = User.query.filter_by(telephone=data["owner"]["telephone"]).first()
    if owner is None:
        owner = User(
            name=data["owner"]["name"],
            telephone=data["owner"]["telephone"],
            description=data["owner"]["description"]
        )

        db.session.add(owner)
        db.session.commit()

    chat = Chat(
        name = data["name"],
        users = [ owner ],
        chat_id = data["owner"]["chat_id"],
        description = data.get("description", None)
    )

    db.session.add(chat)
    db.session.commit()

    opkey = data["user"]["used_keys"][1]
    dh_ratchet_key = data["user"]["used_keys"][0]

    pvt_keys = {
        "IK": crypto.load_private_key("id_key"),
        "SPK": crypto.load_private_key("sgn_key"),
        "OPK": crypto.load_private_key(f"{opkey}_opk")
    }
    dh_ratchet = crypto.load_private_key(f"{dh_ratchet_key}_opk")
    user_ratchet = data["user"]["dh_ratchet"]
    root_ratchet = crypto.create_chat_encryption(
        pvt_keys, data["owner"]["keys"]["pb_keys"], sender=False
    )

    crypto.save_ratchet(chat.id, "dh_ratchet", dh_ratchet)
    crypto.save_ratchet(chat.id, "user_ratchet", user_ratchet)
    crypto.save_ratchet(chat.id, "root_ratchet", root_ratchet)

    sio.emit("confirm-create-chat", {
        "Signed-Message": api.sign_message(),
        "telephone": user.telephone,
        "body": {
            "owner": {
                "telephone": data["owner"]["telephone"],
                "chat_id": data["owner"]["chat_id"]
            },
            "user": {
                "name": user.name,
                "telephone": user.telephone,
                "chat_id": chat.id,
                "keys": {
                    "dh_ratchet": crypto.public_key(dh_ratchet),
                    "OPK": crypto.public_key(pvt_keys["OPK"]),
                    "IK": crypto.public_key(pvt_keys["IK"]),
                    "SPK": crypto.public_key(pvt_keys["SPK"])
                }
            },
        }
    })

@sio.on("confirm-create-chat")
def confirm_create_chat (data: dict) -> None:
    user = User.query.filter_by(telephone=data["user"]["telephone"]).one()
    user.name = data["user"]["name"]

    chat = Chat.query.filter_by(id=data["owner"]["chat_id"])

    db.session.add(user)
    db.session.add(chat)
    db.session.commit()

    eph_key = crypto.load_private_key(f"eph-{chat.id}-{api.user_id}")
    dh_ratchet = crypto.load_private_key(f"dhr-{chat.id}-{api.user_id}")

    user_ratchet = data["user"]["keys"].pop("dh_ratchet")
    user_keys = data["user"]["keys"]
    root_ratchet = crypto.create_chat_encryption(
        { "IK": api.id_key, "EK": eph_key }, pb_keys=user_keys, sender=True
    )

    crypto.save_ratchet(chat.id, "dh_ratchet", dh_ratchet)
    crypto.save_ratchet(chat.id, "user_ratchet", user_ratchet)
    crypto.save_ratchet(chat.id, "root_ratchet", root_ratchet)

    crypto.clean_chat_keys(chat.id, api.user_id)