import dotenv

from pathlib import Path

base_path = Path(__file__).resolve().parent
dotenv.load_dotenv(base_path / ".env", override=False)

from app import flask_app
from app import sio

if __name__ == '__main__':
    sio.run(flask_app, use_reloader=False)