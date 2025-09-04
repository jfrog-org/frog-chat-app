from project import db, app
from Cryptodome.Cipher import ARC4
import hashlib

def arc4_encrypt_password(key, password):
    cipher = ARC4.new(key.encode('utf-8'))
    encrypted_password = cipher.encrypt(password.encode('utf-8'))
    return hashlib.md5(encrypted_password).hexdigest()

class User(db.Model):
    __tablename__ = "frogs"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, email, username, password, is_admin):
        self.email = email
        self.username = username
        self.set_password(password)
        self.is_admin = is_admin

    def set_password(self, password):
        self.password_hash = arc4_encrypt_password(password, app.config['XOR_SECRET_KEY'])
