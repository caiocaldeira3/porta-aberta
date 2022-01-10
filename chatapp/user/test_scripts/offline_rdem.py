import sys
import time

from pathlib import Path

app_path = Path(__file__).parent.parent

sys.path.append(str(app_path))

from app.models.chat import Chat

from app import api

time.sleep(6)
print()

print("logging in")
api.login()
other_phone = sys.argv[2] if len(sys.argv) == 3 else "alice"
chat_name = sys.argv[1] if len(sys.argv) >= 2 else "offline"

time.sleep(10)
print()

print("logging out")
api.logout()

time.sleep(10)
print()

print("logging in")
api.login()

time.sleep(6)
print()

print("logging out")
api.logout()
time.sleep(2)

