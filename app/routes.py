from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.model import User
from app.forms import RegistrationForm, LoginForm

main = Blueprint('main', __name__)

# Page 1 - Landing Page
@main.route('/')
@main.route('/index')
def index():
    # Automatically redirect member to dashboard if already logged in
    if session.get("role") == "member":
        return redirect(url_for("main.dashboard"))
    return render_template("page_1_LandingPage.html")

# Page 2 - Login Page

@main.route("/logout")
def logout():
    role = session.get("role")
    session.clear()
    return redirect(url_for("main.index"))

# Page 3 - Register Page
@main.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    error_msg = None
    success_msg = None

    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.email == form.email.data) |
            (User.contact == form.contact.data)
        ).first()

        if existing_user:
            error_msg = "Email or contact number already exists."
            return render_template("page_3_registerPage.html", form=form, error_msg=error_msg)

        if form.password.data != form.confirm_password.data:
            error_msg = "Passwords do not match. Please try again."
            return render_template("page_3_registerPage.html", form=form, error_msg=error_msg)

        # If all validations pass
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            contact=form.contact.data or None,
            password=hashed_pw
        )

        db.session.add(new_user)
        db.session.commit()

        success_msg = "Account has been created successfully! You can now login."
        return render_template("page_3_registerPage.html", form=RegistrationForm(), success_msg=success_msg)

    return render_template("page_3_registerPage.html", form=form)


# Page 4 - Dashboard Page

# Page 5 - Appointments Manager Page
@main.route("/appointments")
def appointments():
    return render_template("page_5_AppointmentsManagerPage.html")

# Page 6 - Add Appointment Page
@main.route("/appointments/add_appointment")
def add_appointment():
    return render_template("page_6_AddAppointmentPage.html")

# Page 7 - Calendar View Page
@main.route("/calendar")
def calendar():
    return render_template("page_7_CalendarViewPage.html")

# Page 8 - Medical Documents Manager Page
@main.route("/medical_document")
def medical_document():
    return render_template("page_8_MedicalDocumentsManagerPage.html")

# Page 9 - Upload New Document Page
@main.route("/medical_document/upload_document")
def upload_document():
    return render_template("page_9_UploadNewDocumentPage.html")

# Page 10 - Select Documents to Share Page
@main.route("/medical_document/share_document")
def share_document():
    return render_template("page_10_SelectDocumentsToSharePage.html")

# Page 11 - User Profile Settings Page
@main.route("/user_profile")
def user_profile():
    return render_template("page_11_UserProfileSettingsPage.html")

# Page 12 - Edit Appointment Page
@main.route("/appointments/edit_appointment")
def edit_appointment():
    return render_template("page_12_EditAppointmentPage.html")

# Page 13 - Edit Document Page
@main.route("/medical_document/edit_document")
def edit_document():
    return render_template("page_13_EditDocumentPage.html")
