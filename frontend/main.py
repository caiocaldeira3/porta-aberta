from enum import unique
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

import sys
from pathlib import Path

base_path = Path(__file__).resolve().parent.parent
print(base_path)
sys.path.append("/home/nathan/Documentos/nn/UFMG/21-2-REMOTO/es/porta-aberta")

from chatapp.user.app import api 


db = SQLAlchemy()
DB_NAME = "database.db"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'password'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
db.init_app(app)

class User(db.Model):
    name = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.String(255))
   # phone = db.Column(db.String(255), unique=True)

db.create_all(app=app)
current_user = ""

@app.route('/home')
def home():
    global current_user
    return render_template('home.html',current_user=current_user)

@app.route('/register')
def register():
    return render_template('register.html')
    
@app.route("/",methods=['GET', 'POST'])

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

@app.route("/profile")
def profile():
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
