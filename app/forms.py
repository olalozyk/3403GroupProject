from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models import User,Document


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
    remember_me = BooleanField("Remember Me")


class RegistrationForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), EqualTo("password", message="Passwords must match.")
    ])
    submit = SubmitField("Register")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email is already registered. Please use a different email address.')


class DocumentForm(FlaskForm):
    upload_document = FileField(
        'Choose File',
        validators=[
            FileRequired(message="A file is required."),
            FileAllowed(['pdf', 'doc', 'docx', 'txt', 'jpg', 'png','zip'],
                        message="Only PDF, DOC/DOCX, TXT, JPG or PNG allowed.")
        ]
    )
    document_name = StringField("Document Name", validators=[DataRequired()])
    upload_date = DateField("Upload Date", validators=[DataRequired()])
    document_type = StringField("Document Type", validators=[DataRequired()])
    document_notes = TextAreaField('Notes', validators=[Optional()])
    practitioner_name = StringField("Practitioner Name", validators=[DataRequired()])
    expiration_date = DateField("Expiration Date", validators=[Optional()])
    practitioner_type = StringField("Practitioner Type", validators=[DataRequired()])

class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')