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
    
@app.route("/",methods=['GET', 'POST'])
def index():
    print("TAMO RODANDOAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    if request.method == 'POST':
        email = request.form["user"]
        passwd = request.form["passwd"]
        print("RODEIaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        return redirect(url_for('home'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
