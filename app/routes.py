from flask import render_template, flash, redirect, url_for, request, session, jsonify, g, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf.csrf import validate_csrf, CSRFError
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, Document, Appointment
from datetime import datetime, timedelta, time, date

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
        if user and user.check_password(form.password.data):
            login_user(user)

            session['user_id'] = user.id
            session['first_name'] = user.first_name
            session['role'] = user.role

            # Sync session with DB-stored notification viewed_at
            session['notifications_viewed_at'] = (
                user.notifications_viewed_at.isoformat()
                if user.notifications_viewed_at else datetime.min.isoformat()
            )

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
    if session.get("role") != "member":
        return redirect(url_for("login"))

    today = datetime.today().date()

    upcoming_appointments = (
        Appointment.query
        .filter(
            Appointment.user_id == session["user_id"],
            Appointment.appointment_date >= today
        )
        .order_by(Appointment.appointment_date.asc())
        .limit(5)
        .all()
    )

    upcoming_data = []
    for appt in upcoming_appointments:
        days_away = (appt.appointment_date - today).days
        upcoming_data.append({
            "days_away": days_away,
            "date": appt.appointment_date.strftime("%b %d"),
            "practitioner": appt.practitioner_name,
            "type": appt.practitioner_type,
            "start_time": appt.starting_time.strftime("%I:%M%p").lower(),
            "end_time": appt.ending_time.strftime("%I:%M%p").lower()
        })

    # Expiring documents
    expiring_docs = (
        db.session.query(Document, Appointment)
        .join(Appointment, Document.appointment_id == Appointment.id)
        .filter(
            Document.user_id == session["user_id"],
            Document.expiration_date != None,
            Document.expiration_date >= today
        )
        .order_by(Document.expiration_date.asc())  # sort by soonest
        .limit(5)  # <- only top 5
        .all()
    )

    expiring_data = []
    for doc, appt in expiring_docs:
        days_left = (doc.expiration_date - today).days
        expiring_data.append({
            "days_left": days_left,
            "document_type": doc.document_type,
            "practitioner_type": appt.practitioner_type,
            "expires_on": doc.expiration_date.strftime("%b %d")
        })

    return render_template(
        "page_4_dashboardPage.html",
        upcoming_appointments=upcoming_data,
        expiring_docs=expiring_data  # Include this line
    )

@app.route("/notifications/read", methods=["POST"])
def mark_notifications_read():
    try:
        csrf_token = request.headers.get("X-CSRFToken")
        validate_csrf(csrf_token)
    except CSRFError:
        return "CSRF token invalid or missing", 400

    timestamp = datetime.utcnow()
    session["notifications_viewed_at"] = timestamp.isoformat()

    if current_user.is_authenticated:
        current_user.notifications_viewed_at = timestamp
        db.session.commit()

    session.modified = True
    return jsonify({"success": True})


@app.context_processor
def inject_notifications():
    notifications = []
    n_not = 0

    if session.get("role") == "member" and "user_id" in session:
        user_id = session["user_id"]
        now = datetime.now()

        appointments = Appointment.query.filter(
            Appointment.user_id == user_id,
            Appointment.appointment_date >= now.date()
        ).all()

        reminder_options = {
            "2 hours before": timedelta(hours=2),
            "12 hours before": timedelta(hours=12),
            "1 day before": timedelta(days=1),
            "1 week before": timedelta(weeks=1),
        }

        for appt in appointments:
            appt_datetime = datetime.combine(appt.appointment_date, appt.starting_time)

            # Standard reminders
            reminder_list = appt.reminder.split(",") if appt.reminder else []
            for rem in reminder_list:
                rem = rem.strip()
                if rem in reminder_options:
                    reminder_time = appt_datetime - reminder_options[rem]
                    if reminder_time <= now:
                        notifications.append({
                            "title": "Upcoming Appointment",
                            "body": f"{appt.practitioner_name} ({appt.practitioner_type})",
                            "date": appt.appointment_date.strftime("%b %d"),  # Correct: appointment date
                            "reminder_info": f"{rem}",  # e.g. "1 day before"
                            "triggered_on": reminder_time.strftime("%b %d"),  # the day it popped up
                        })

            # Custom reminder
            if appt.custom_reminder:
                custom_reminder_time = datetime.combine(appt.custom_reminder, time.min)
                if custom_reminder_time <= now:
                    notifications.append({
                        "title": "Reminder",
                        "body": f"{appt.practitioner_name}",
                        "date": appt.appointment_date.strftime("%b %d"),
                        "reminder_info": "Custom reminder for",
                        "reminder_date": appt.custom_reminder.strftime("%b %d"),
                        "triggered_on": custom_reminder_time.strftime("%b %d"),
                        "timestamp": custom_reminder_time
                    })

        n_not = len(notifications)  # badge will now show ALL relevant notifications

    return dict(n_not=n_not, notifications=notifications)

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
        
        flash("Appointment successfully created", "success")
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
        flash("Appointment successfully updated", "success")
        return redirect(url_for("appointment_manager"))

    return render_template("page_6_AddAppointmentPage.html", appt=appt, is_edit=True)


@app.route("/appointment/delete/<int:appointment_id>", methods=["POST"])
def delete_appointment(appointment_id):
    appt = Appointment.query.get_or_404(appointment_id)

    if session.get("role") != "member" or appt.user_id != session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(appt)
    db.session.commit()
    flash("Appointment successfully deleted", "success")
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

# Delete document route
@app.route("/medical_document/delete/<int:doc_id>")
@login_required
def delete_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    if document.user_id != current_user.id:
        flash("You don't have permission to delete this document")
        return redirect(url_for('medical_document'))
    db.session.delete(document)
    db.session.commit()

    flash(f"Document '{document.document_name}' has been deleted")
    return redirect(url_for('medical_document'))

# Page 9 - Upload New Document Page
@app.route("/medical_document/upload_document")
@login_required
def upload_document():
    return render_template("page_9_UploadNewDocumentPage.html")

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
@app.route("/medical_document/edit_document")
@login_required
def edit_document():
    return render_template("page_13_EditDocumentPage.html")