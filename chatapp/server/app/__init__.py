# Import flask and template operators
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Import Migration Module
from flask_migrate import Migrate

# Import Util Modules
# from app.util.responses import NotFoundError

# Define the WSGI application object
flask_app = Flask(__name__)
CORS(flask_app)

# Configurations
flask_app.config.from_object('config')
sio = SocketIO(flask_app, async_mode="eventlet")

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(flask_app)
migrate = Migrate(flask_app, db)

# Sample HTTP error handling
#@app.errorhandler(404)
#def not_found (error: Exception) -> wrappers.Response:
#    return NotFoundError

# Import a module / component using its blueprint handler variable (mod_auth)
import app.modules.auth.events
import app.modules.user.events

# Build the database:
# This will create the database file using SQLAlchemy

db.create_all()