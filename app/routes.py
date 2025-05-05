from flask import render_template, flash, redirect, url_for, request, session, jsonify, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import app, db
from app.forms import LoginForm, RegistrationForm, DocumentForm
from app.models import User, Document, Appointment
from datetime import datetime
from sqlalchemy import asc, desc, nulls_last
import os


# Page 1 - Landing Page
@app.route('/')
@app.route('/index')
def index():
    # Automatically redirect member to dashboard if already logged in
    if session.get("role") == "member":
        return redirect(url_for("dashboard"))
    return render_template("page_1_LandingPage.html")

# Page 2 - Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    msg = ""

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):  # use method
            login_user(user)  # Flask-Login login
            session['user_id'] = user.id
            session['first_name'] = user.first_name
            session['role'] = user.role
            flash("Login successful", "success")
            return redirect(url_for('dashboard'))
        else:
            msg = "Invalid email or password"

    return render_template("page_2_loginPage.html", form=form, msg=msg)

@app.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("index"))

# Page 3 - Register Page
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        # All validations passed, create new user
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=hashed_pw,
            role="member"  # Make sure to set a default role
        )

        db.session.add(new_user)
        db.session.commit()

        success_msg = "Account has been created successfully! You can now login."
        return render_template("page_3_registerPage.html", form=RegistrationForm(), success_msg=success_msg)

    return render_template("page_3_registerPage.html", form=form)

# Page 4 - Dashboard Page
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("page_4_dashboardPage.html")

# Page 5 - Appointments Manager Page
@app.route("/appointments")
def appointment_manager():
    if session.get("role") != "member":
        return redirect(url_for("login"))

    sort_by = request.args.get("sort", "appointment_date")
    order = request.args.get("order", "asc")

    appointments = Appointment.query.filter_by(user_id=session["user_id"])

    if sort_by == "appointment_date":
        appointments = appointments.order_by(
            Appointment.appointment_date.asc() if order == "asc" else Appointment.appointment_date.desc()
        )

    return render_template("page_5_AppointmentsManagerPage.html", appointments=appointments.all())

@app.route("/appointment/add", methods=["GET", "POST"])
def add_appointment():
    if request.method == "POST":
        # Directly get start_time and end_time from the form
        start_time_str = request.form['starting_time']
        end_time_str = request.form['ending_time']

        # Parse them properly
        starting_time = datetime.strptime(start_time_str, "%H:%M").time()
        ending_time = datetime.strptime(end_time_str, "%H:%M").time()

        # Reminder handling
        reminder = ",".join(request.form.getlist("reminder"))
        reminder_custom_str = request.form.get("custom_reminder")
        custom_reminder = datetime.strptime(reminder_custom_str, "%Y-%m-%d").date() if reminder_custom_str else None

        # Create the appointment
        new_appointment = Appointment(
            user_id=session["user_id"],
            appointment_date=datetime.strptime(request.form['appointment_date'], "%Y-%m-%d").date(),
            starting_time=starting_time,
            ending_time=ending_time,
            practitioner_name=request.form['practitioner_name'],
            practitioner_type=request.form['practitioner_type'],
            location=request.form['location'],
            appointment_notes=request.form['appointment_notes'],
            appointment_type=request.form['appointment_type'],
            provider_number=request.form.get('provider_number'),
            reminder=reminder,
            custom_reminder=custom_reminder
        )

        # Save to DB
        db.session.add(new_appointment)
        db.session.commit()

        return redirect(url_for("appointment_manager"))

    # GET method — show blank form
    return render_template("page_6_AddAppointmentPage.html", appt=None, is_edit=False)

@app.route("/appointment/edit/<int:appointment_id>", methods=["GET", "POST"])
def edit_appointment(appointment_id):
    appt = Appointment.query.get_or_404(appointment_id)

    if session.get("role") != "member" or appt.user_id != session.get("user_id"):
        return redirect(url_for("login"))

    if request.method == "POST":
        # NEW: Fetch start_time and end_time separately (NO more time split)
        start_time_str = request.form["starting_time"]
        end_time_str = request.form["ending_time"]

        starting_time = datetime.strptime(start_time_str.strip(), "%H:%M").time()
        ending_time = datetime.strptime(end_time_str.strip(), "%H:%M").time()

        # Update appointment fields
        appt.appointment_date = datetime.strptime(request.form["appointment_date"], "%Y-%m-%d").date()
        appt.starting_time = starting_time
        appt.ending_time = ending_time
        appt.practitioner_name = request.form["practitioner_name"]
        appt.practitioner_type = request.form["practitioner_type"]
        appt.location = request.form["location"]
        appt.appointment_notes = request.form["appointment_notes"]
        appt.appointment_type = request.form["appointment_type"]
        appt.provider_number = request.form.get("provider_number")
        appt.reminder = ",".join(request.form.getlist("reminder"))

        reminder_custom_str = request.form.get("custom_reminder")
        appt.custom_reminder = datetime.strptime(reminder_custom_str, "%Y-%m-%d").date() if reminder_custom_str else None

        db.session.commit()
        return redirect(url_for("appointment_manager"))

    return render_template("page_6_AddAppointmentPage.html", appt=appt, is_edit=True)

@app.route("/appointment/delete/<int:appointment_id>", methods=["POST"])
def delete_appointment(appointment_id):
    appt = Appointment.query.get_or_404(appointment_id)

    if session.get("role") != "member" or appt.user_id != session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(appt)
    db.session.commit()
    return jsonify({"success": True})

# Page 7 - Calendar View Page
@app.route("/calendar")
@login_required
def calendar():
    return render_template("page_7_CalendarViewPage.html")

# Page 8 - Medical Documents Manager Page
@app.route("/medical_document")
@login_required
def medical_document():
    # Get all documents for the current user
    documents = Document.query.filter_by(user_id=current_user.id).all()

    # Handle sorting parameter if provided
    sort_by = request.args.get('sort', 'upload-desc')

    if sort_by == 'upload-asc':
        documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.upload_date.asc()).all()
    elif sort_by == 'upload-desc':
        documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.upload_date.desc()).all()
    elif sort_by == 'expiry-asc':
        documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.expiration_date.asc()).all()
    elif sort_by == 'expiry-desc':
        documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.expiration_date.desc()).all()

    return render_template("page_8_MedicalDocumentsManagerPage.html", documents=documents, sort_by=sort_by)

# View document route
@app.route("/medical_document/view/<int:doc_id>")
@login_required
def view_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    if document.user_id != current_user.id:
        flash("You don't have permission to view this document")
        return redirect(url_for('medical_document'))
    # for now return to the documents list with a message
    flash("Document viewing functionality will be implemented soon")
    return redirect(url_for('medical_document'))

# Download document route
@app.route("/medical_document/download/<int:doc_id>")
@login_required
def download_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    if document.user_id != current_user.id:
        flash("You don't have permission to download this document")
        return redirect(url_for('medical_document'))
    flash("Document download functionality will be implemented soon")
    return redirect(url_for('medical_document'))


# Page 9 - Upload New Document Page

@app.route("/medical_document/upload_document", methods=["GET", "POST"])
@login_required
def upload_document():
    form = DocumentForm()

    if form.validate_on_submit():
        # 1. Get the file and save it
        file_field = form.upload_document.data
        filename   = secure_filename(file_field.filename)
        save_path  = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file_field.save(save_path)

        # 2. Build your Document model from form data
        new_doc = Document(
            user_id=current_user.id,
            file=filename,
            document_name    = form.document_name.data,
            upload_date      = form.upload_date.data,
            document_type    = form.document_type.data,
            document_notes   = form.document_notes.data,
            practitioner_name= form.practitioner_name.data,
            expiration_date  = form.expiration_date.data,
            practitioner_type= form.practitioner_type.data
        )

        # 3. Commit to the database
        db.session.add(new_doc)
        db.session.commit()

        flash("Document uploaded successfully!", "success")
        return redirect(url_for("medical_document"))

    # If GET, or if validation failed, render the template with the form
    return render_template(
        "page_9_UploadNewDocumentPage.html",
        form=form
    )

# Page 10 - Select Documents to Share Page
@app.route("/medical_document/share_document")
@login_required
def share_document():
    return render_template("page_10_SelectDocumentsToSharePage.html")

# Page 11 - User Profile Settings Page
@app.route("/user_profile")
@login_required
def user_profile():
    return render_template("page_11_UserProfileSettingsPage.html")


# Page 13 - Edit Document Page
# Page 13 - Edit Document Page
@app.route("/medical_document/edit_document/<int:doc_id>", methods=["GET", "POST"])
@login_required
def edit_document(doc_id):
    document = Document.query.get_or_404(doc_id)

    form = DocumentForm(obj=document)

    if form.validate_on_submit():
        file_field = form.upload_document.data

        # Check if the user selected a new file
        if file_field:
            filename = secure_filename(file_field.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file_field.save(save_path)
            document.file = filename  # Update the file field with the new file
        else:
            # If no new file is selected, retain the existing file in the database
            document.file = document.file

        # Update other fields
        document.document_name = form.document_name.data
        document.upload_date = form.upload_date.data
        document.document_type = form.document_type.data
        document.document_notes = form.document_notes.data
        document.practitioner_name = form.practitioner_name.data
        document.expiration_date = form.expiration_date.data
        document.practitioner_type = form.practitioner_type.data

        db.session.commit()

        flash("Document edited successfully!", "success")
        return redirect(url_for("medical_document"))

    return render_template(
        "page_13_EditDocumentPage.html",
        form=form,
        document=document
    )