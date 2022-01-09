import threading
import socketio

# Import flask and template operators
from flask import Flask
from flask_cors import CORS
from flask import render_template, request, redirect, url_for

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Import Migration Module
from flask_migrate import Migrate

# Import Util Modules

# from app.util.responses import NotFoundError

# Define the WSGI application object
flask_app = Flask(__name__, static_url_path = "/app/static")
CORS(flask_app)

sio = socketio.Client()

# Configurations
flask_app.config.from_object("config")
current_user = ""

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(flask_app)
migrate = Migrate(flask_app, db)

# Sample HTTP error handling
#@app.errorhandler(404)
#def not_found (error: Exception) -> wrappers.Response:
#    return NotFoundError

# Import a module / component using its blueprint handler variable (mod_auth)
from app.util.jobs import JobQueue
job_queue = JobQueue()

from app.util.api import Api
api = Api()

import app.modules.auth.events
import app.modules.user.events

from app.modules.auth.controller import mod_auth as auth_module
from app.modules.user.controller import mod_user as user_module

# Register blueprint(s)
# ..
flask_app.register_blueprint(auth_module)
flask_app.register_blueprint(user_module)

# Build the database:
# This will create the database file using SQLAlchemy

db.create_all()
threading.Thread(target=api.job_handler, daemon=True).start()
