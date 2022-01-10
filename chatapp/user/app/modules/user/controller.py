from flask import Blueprint, render_template, request, redirect, url_for

from app.util.messages import messages

from app import current_user
from app import api

mod_user = Blueprint("user", __name__, url_prefix="/user")

chats = []
current_chat = ""
current_user_name = "Usuário"

@mod_user.route('/home',methods=['GET', 'POST'])
def home():

    global current_user
    chat_id = 0

    def create_chat(chatname,guestphone):
        chats.append(chatname)
        global current_chat
        current_chat = chatname
        chat_id = api.create_chat(chatname,int(guestphone))

    def send_message():
        global message
        message = request.form["message"]
        api.send_message(chat_id, message)
        messages.append(["message_me",message])

    def change_chat():
        global current_chat, messages
        current_chat = chats[int(request.form["button"])]
        messages = []

    if request.method == 'POST':
        if request.form["button"] == "Novo Chat":
            create_chat(request.form["chatname"],request.form["guestphone"])
        elif request.form["button"] == "Enviar":
            send_message()
        else:
            change_chat()

    return render_template('home.html', current_chat=current_chat, current_user_name=current_user_name,messages=messages,chats=chats,len_messages=len(messages),len_chats=len(chats))

@mod_user.route("/profile")
def profile():
    return render_template('profile.html')