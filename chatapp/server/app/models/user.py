from app import db

# Define a User model
class User (db.Model):

    __tablename__   : str = "user"
    id              : db.Integer = db.Column(db.Integer, primary_key=True)

    # User Name
    name            : db.String = db.Column(db.String(128), nullable=False)

    # Identification Data: email & password
    telephone       : db.String = db.Column(db.String(15), nullable=False, unique=True)
    id_key          : db.String = db.Column(db.String(128), nullable=False)
    sgn_key         : db.String = db.Column(db.String(128), nullable=False)
    ed_key          : db.String = db.Column(db.String(128), nullable=False)

    date_created    : db.DateTime = db.Column(db.DateTime, default=db.func.now())
    date_modified   : db.DateTime = db.Column(
        db.DateTime,  default=db.func.now(), onupdate=db.func.now()
    )

    # Extra Information
    email           : db.String = db.Column(db.String(128), nullable=True, unique=True)
    description     : db.Text = db.Column(db.Text(500), nullable=True)

    # Foreign Keys
    opkeys          : any = db.relationship("OPKey", backref="owner")
    devices         : any = db.relationship("Device", backref="user")

    def __repr__ (self) -> str:
        return f"<User {self.name}>"
