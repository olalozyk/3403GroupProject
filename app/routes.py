import os
import zipfile
import io
from flask import send_file, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from app import app, db
from app.models import Document, Users
from datetime import datetime

# Page 1 - Landing Page
@app.route('/')
@app.route('/index')
def index():
    return render_template("page_1_LandingPage.html")

# Page 2 - Login Page
@app.route("/login")
def login():
    return render_template("page_2_loginPage.html")

# Page 3 - Register Page
@app.route("/register")
def register():
    return render_template("page_3_registerPage.html")

# Page 4 - Dashboard Page
@app.route("/dashboard")
def dashboard():
    return render_template("page_4_dashboardPage.html")

# Page 5 - Appointments Manager Page
@app.route("/appointments")
def appointments():
    return render_template("page_5_AppointmentsManagerPage.html")

# Page 6 - Add Appointment Page
@app.route("/appointments/add_appointment")
def add_appointment():
    return render_template("page_6_AddAppointmentPage.html")

# Page 7 - Calendar View Page
@app.route("/calender")
def calender():
    return render_template("page_7_CalendarViewPage.html")

# Page 8 - Medical Documents Manager Page
@app.route("/medical_document")
def medical_document():
    return render_template("page_8_MedicalDocumentsManagerPage.html")

# Page 9 - Upload New Document Page
@app.route("/medical_document/upload_document")
def upload_document():
    return render_template("page_9_UploadNewDocumentPage.html")

# Page 10 - Select Documents to Share Page
@app.route("/medical_document/share_document")
def share_document():
    return render_template("page_10_SelectDocumentsToSharePage.html")

@app.route('/documents/export', methods=['POST'])
@login_required
def export_documents():
    selected_ids = request.form.getlist('document_ids')
    include_personal_summary = request.form.get('include_personal_summary')

    if not selected_ids:
        flash('No documents selected for export.', 'danger')
        return redirect(url_for('share_document'))

    # Set up an in-memory ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for doc_id in selected_ids:
            doc = Document.query.filter_by(id=doc_id, owner_id=current_user.id).first()
            if not doc:
                continue  # skip if doc not found or not owned by user

            file_path = os.path.join(app.root_path, 'static', 'documents', doc.filename)
            if os.path.exists(file_path):
                zipf.write(file_path, arcname=doc.filename)
            else:
                app.logger.warning(f"File not found: {file_path}")

        # Add personal summary if requested
        if include_personal_summary:
            personal_details = generate_personal_summary(current_user)
            zipf.writestr('PersonalDetails.txt', personal_details)

    zip_buffer.seek(0)
    filename = f"SharedDocuments_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip"

    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )

def generate_personal_summary(user):
    summary = f"""
    Personal Details Summary
    ------------------------
    Name: {user.first_name} {user.last_name}
    Email: {user.email}
    Date of Birth: {user.date_of_birth}
    Contact Number: {user.contact_number}
    Medical Summary:
    {user.medical_summary}

    Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
    """
    return summary

# Page 11 - User Profile Settings Page
@app.route("/user_Profile")
def user_Profile():
    return render_template("page_11_UserProfileSettingsPage.html")

# Page 12 - Edit Appointment Page
@app.route("/appointments/edit_appointment")
def edit_appointment():
    return render_template("page_12_EditAppointmentPage.html")

# Page 13 - Edit Document Page
@app.route("/medical_document/edit_document")
def edit_document():
    return render_template("page_13_EditDocumentPage.html")

# Page 14 - Edit Personalised User Analytics Page
@app.route("/insights")
@login_required
def insights():
    # Placeholder summary data
    total_appointments = 12
    documents_expiring_soon = 3
    most_frequent_practitioner = "Dr Jessica Adams"

    # (Later: Replace these with real database queries!)

    return render_template(
        "page_14_PersonalisedUserAnalytics.html",
        total_appointments=total_appointments,
        documents_expiring_soon=documents_expiring_soon,
        most_frequent_practitioner=most_frequent_practitioner
    )
