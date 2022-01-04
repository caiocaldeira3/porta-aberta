from app import db

# Define a Device model
class Device (db.Model):

    __tablename__   : str = "device"
    id              : db.Integer = db.Column(db.Integer, primary_key=True)

    user_id         : db.Integer = db.Column(db.Integer, db.ForeignKey("user.id"))
    socket_id       : db.String = db.Column(db.String(64), nullable=False)

    def __repr__ (self) -> str:
        return f"<Device {self.socket_id}>"
