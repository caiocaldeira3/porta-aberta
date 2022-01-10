import sys
import time

from pathlib import Path

app_path = Path(__file__).parent.parent

sys.path.append(str(app_path))

from app import api

print("wait for authentication")

if len(sys.argv) == 2:
    print("creating user")
    user_name = "user"
    user_phone = sys.argv[1]
    user_pass = "***"

    api.signup(user_name, user_phone, user_pass)
    time.sleep(5)
    print()

    print("resetting session")
    time.sleep(10)
    print()

else:
    api.login()
    time.sleep(5)

print("wait for logout")
api.logout()

time.sleep(5)
print()

print("wait for authentication")
api.login()

time.sleep(5)

api.logout()