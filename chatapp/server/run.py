import os
import sys
import atexit
import dotenv

from pathlib import Path

base_path = Path(__file__).resolve().parent
dotenv.load_dotenv(base_path / ".env", override=False)

sys.path.append(str(base_path))

from app.models.device import Device

from app import db
from app import sio
from app import flask_app

def exit_handler():
    Device.query.delete()
    db.session.commit()

atexit.register(exit_handler)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    sio.run(flask_app, host="0.0.0.0", port=port, use_reloader=False)