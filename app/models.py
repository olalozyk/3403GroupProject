from sqlalchemy import ForeignKey
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import time, date

class Users(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(25), nullable=False, default="member")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_member_id(self):
        import random
        import string
        member_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        while Users.query.filter_by(member_id=member_id).first() is not None:
            member_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return member_id

    def __repr__(self):
        return f'<User {self.email}>'


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    practitioner_type = db.Column(db.String(100), nullable=False)
    practitioner_name = db.Column(db.String(100), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    starting_time = db.Column(db.Time, nullable=False)
    ending_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    provider_number = db.Column(db.Integer, nullable=True)
    appointment_type = db.Column(db.String(100), nullable=False)
    appointment_notes = db.Column(db.String(1000), nullable=False)
    custom_reminder = db.Column(db.Date, nullable=False)


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)
    file = db.Column(db.String(200), nullable=False)
    document_name = db.Column(db.String(100), nullable=False)
    upload_date = db.Column(db.Date, nullable=False)
    document_type = db.Column(db.String(100), nullable=False)
    document_notes = db.Column(db.String(1000), nullable=False)
    expiration_date = db.Column(db.Date, nullable=True)


class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    mobile_number = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)