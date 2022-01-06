from flask import Flask, render_template, request, redirect, url_for
#from datetime import MAXYEAR
#from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.sql import func
#import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'password'

@app.route('/home')
def home():
    return render_template('home.html')
    
##############################
@app.route("/",methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form["user"]
        passwd = request.form["passwd"]
        print(email)
        return redirect(url_for('home'))

    return render_template('index.html')
######################3

##############################
@app.route("/profile",methods=['GET', 'POST'])
def profile():
    numero = 509
    return render_template('profile.html',numero=numero)
######################3

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
