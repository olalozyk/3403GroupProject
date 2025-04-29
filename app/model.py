from flask_login import UserMixin
from app.extensions import db, login_manager

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contact = db.Column(db.String(150), unique=True, nullable=True)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="member")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))