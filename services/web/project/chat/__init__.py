from flask import Blueprint

chat_blueprint = Blueprint('chat', __name__)
rooms = {}
files = []

from . import views
