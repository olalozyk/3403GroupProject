from app import db

class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100),unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    confirm_password = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)
    contact_number = db.Column(db.String(20))
    medical_summary = db.Column(db.Text)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    filepath = db.Column(db.String(300), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
