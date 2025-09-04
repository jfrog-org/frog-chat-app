from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object("project.config.Config")
app.config.update(
    SESSION_COOKIE_HTTPONLY=False
)
app.secret_key = "S3cr3tKey"
db = SQLAlchemy(app)
socketio = SocketIO(app)

from project.auth.views import auth_blueprint
from project.chat.views import chat_blueprint
from project.admin.views import admin_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(chat_blueprint)
app.register_blueprint(admin_blueprint)

from .models import User
