from app import db

# Define a Message model
class Message (db.Model):

    __tablename__   : str = "message"
    id          : db.Integer = db.Column(db.Integer, primary_key=True)

    # Message Content
    message         : db.Text = db.Column(db.Text(500), nullable=False)
    time_sent       : db.DateTime = db.Column(db.DateTime, default=db.func.current_timestamp())

    user_id         : db.Integer = db.Column(db.Integer, db.ForeignKey("user.id"))
    chat_id         : db.Integer = db.Column(db.Integer, db.ForeignKey("chat.id"))

    def __repr__ (self) -> str:
        return f"<Message from {self.sender.name}>"
