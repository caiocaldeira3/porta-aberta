import sys
import time

from pathlib import Path

app_path = Path(__file__).parent.parent

sys.path.append(str(app_path))

from app.models.chat import Chat
from app.models.user import User

from app import api

time.sleep(5)

api.login()
other_phone = sys.argv[2] if len(sys.argv) == 3 else "alice"
chat_name = sys.argv[1] if len(sys.argv) >= 2 else "server"

time.sleep(5)
user = User.query.filter_by(id=api.user_id).one()
print(f"Other phone should be {user.telephone}")

time.sleep(10)

time.sleep(5)

print("sending message")
chat = Chat.query.filter_by(name=chat_name).one()
api.send_message(chat.id, "eai alicee! tudo bem?", debug=True)

time.sleep(10)
api.logout()