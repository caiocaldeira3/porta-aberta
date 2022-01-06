from app import db

from . import user_chat

# Define a Chat model
class Chat (db.Model):

    __tablename__   : str = "chat"
    id              : db.Integer = db.Column(db.Integer, primary_key=True)

    # Chat Name
    name            : db.String = db.Column(db.String(128), nullable=False)
    date_created    : db.DateTime = db.Column(db.DateTime, default=db.func.now())
    date_modified   : db.DateTime = db.Column(
        db.DateTime,  default=db.func.now(), onupdate=db.func.now()
    )

    # Chat ID from other users
    # TODO -> Make it a list or a hash to unify
    chat_id         : db.Integer = db.Column(db.Integer, nullable=True)

    # Extra Information
    description     : db.Text = db.Column(db.Text(500), nullable=True)

    # Foreign Keys
    # messages       : any = db.relationship("Message", backref="sender")
    users           : any = db.relationship(
        "User", secondary=user_chat, backref=db.backref("chats", lazy="dynamic")
    )

    def __repr__ (self) -> str:
        return f"<Chat {self.name}>"
