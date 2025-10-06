from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

from models.connection import db
from models.model import User
from routes.api import app as bp_api
from routes.auth import app as bp_auth
from routes.admin import app as bp_admin
from routes.default import app as bp_default

load_dotenv()

app = Flask(__name__, instance_relative_config=True)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///labo1.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id: str):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None



app.register_blueprint(bp_api, url_prefix="/api")
app.register_blueprint(bp_auth, url_prefix="/")
app.register_blueprint(bp_admin, url_prefix="/admin")
app.register_blueprint(bp_default, url_prefix="/")


if __name__ == '__main__':
    debug_flag = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug_flag)