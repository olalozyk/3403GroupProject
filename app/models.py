from sqlalchemy import ForeignKey
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, time, datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # still stores a hash!
    notifications_viewed_at = db.Column(db.DateTime, default=datetime.min)
    role = db.Column(db.String(25), nullable=False, default="member")

    appointments = db.relationship("Appointment", backref="user", lazy='dynamic')
    documents = db.relationship("Document", backref="user", lazy='dynamic')
    profile = db.relationship("UserProfile", backref="user", uselist=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.email}>'
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    practitioner_type = db.Column(db.String(100), nullable=False)
    practitioner_name = db.Column(db.String(100), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    starting_time = db.Column(db.Time, nullable=False)
    ending_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    provider_number = db.Column(db.Integer, nullable=True)
    appointment_type = db.Column(db.String(100), nullable=False)
    appointment_notes = db.Column(db.String(1000), nullable=False)
    reminder = db.Column(db.Text)  # store comma-separated reminders
    custom_reminder = db.Column(db.Date, nullable=True)


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    file = db.Column(db.String(200), nullable=False)
    document_name = db.Column(db.String(100), nullable=False)
    upload_date = db.Column(db.Date, nullable=False)
    document_type = db.Column(db.String(100), nullable=False)
    document_notes = db.Column(db.String(1000), nullable=False)
    practitioner_name = db.Column(db.String(100), nullable=False)
    expiration_date = db.Column(db.Date, nullable=True)
    practitioner_type = db.Column(db.String(100), nullable=True)

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    mobile_number = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


# Required by Flask-Login
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

