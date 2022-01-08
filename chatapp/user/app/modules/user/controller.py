from flask import Blueprint, render_template

from app import current_user

mod_user = Blueprint("user", __name__, url_prefix="/user")

@mod_user.route('/home')
def home():
    global current_user
    return render_template('home.html', current_user=current_user)

@mod_user.route("/profile")
def profile():
    return render_template('profile.html')