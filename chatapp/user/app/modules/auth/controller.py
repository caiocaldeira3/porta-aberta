from flask import Blueprint, render_template, request, redirect, url_for

from app.models.user import User

from app import db
from app import api

mod_auth = Blueprint("auth", __name__, url_prefix="/auth")

@mod_auth.route("/register")
def register():
    return render_template("register.html")


@mod_auth.route("/",methods=['GET', 'POST'])
def index():

    warning = ""

    def register():

        records = db.session.query(User).filter_by(name=name).first()
        if records is not None:
            return "usuário ja existe"

        user = User(name = name, password = password)
        db.session.add(user)
        db.session.commit()
        return "registrado"

    def login():
        records = db.session.query(User).filter_by(name=name).first()
        if records is None:
            return "usuário não existe"

        true_password = records.password
        if password == true_password:
            global current_user
            current_user = name
            return "ok"
        else:
            warning = "senha incorreta"
            return warning

    if request.method == 'POST':

        name = request.form["name"]
        password = request.form["password"]

        if name == ""  or password == "":
            warning = "campo vazio"
        else:
            if request.form["button"] == "Login":
                warning = login()
            else:
                warning = register()

        if warning == "ok":
            return redirect(url_for('home'))
        elif warning == "logged_in":
            api.login()
            return redirect(url_for('home'))
        elif warning == "registered":
            api.signup(name, name, password)
            return redirect(url_for('home'))

    return render_template('index.html',warning=warning)