from app import db
from app.models import user_chat

# Define a User model
class User (db.Model):

    __tablename__   : str = "user"
    id              : db.Integer = db.Column(db.Integer, primary_key=True)

    # User Name
    name            : db.String = db.Column(db.String(128), nullable=True)

    # Identification Data: email & telephone & password & id on server
    email           : db.String = db.Column(db.String(128), nullable=True, unique=True)
    telephone       : db.String = db.Column(db.String(15), nullable=False, unique=True)
    password        : db.String = db.Column(db.String(128), nullable=True)

    # Attributes
    description     : db.String = db.Column(db.String(255), nullable=True)

    # Foreign Keys
    # messages        : any = db.relationship("Message", backref="sender")

    def __repr__ (self) -> str:
        return f"<User {self.name}>"
