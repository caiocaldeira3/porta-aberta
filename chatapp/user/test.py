from app import api
from app.models.user import User

action = ""
while action != "exit":
    if action == "login":
        api.login()

    elif action == "logout":
        api.logout()

    elif action == "signup":
        name = input("username: ")
        phone = input("telephone: ")
        password = input("password: ")

        api.signup(name, phone, password)

    elif action == "create-chat":
        name = input("chatname: ")
        user_phone = input("target user phone: ")

        api.create_chat(name, [ user_phone ])

    elif action == "send-message":
        chat_id = input("chat_id: ")
        message = input("message: ")

        api.send_message(chat_id, message)

    elif action == "info":
        print(f"user_id: {api.user_id}")
        user = User.query.filter_by(id=api.user_id).one()
        print(f"user-name: {user.name} | user-phone: {user.telephone}")

    else:
        print("Available actions:")
        print("login | logout | signup | create-chat | send-message | info")

    action = input("action: ")

api.logout()