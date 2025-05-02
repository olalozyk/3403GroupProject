from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, Document
from datetime import datetime
# Page 1 - Landing Page
@app.route('/')
@app.route('/index')
def index():
    return render_template("page_1_LandingPage.html")

# Page 2 - Login Page
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        
        if not user.member_id:
            user.member_id = user.generate_member_id()
            db.session.commit()
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard')
        return redirect(next_page)
    
    return render_template("page_2_LoginPage.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

# Page 3 - Register Page
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            member_id=form.member_id.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            role="member"
        )
        user.set_password(form.password.data)

        # Generate and set member_id
        user.member_id = user.generate_member_id()
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in with your new account.')
        return redirect(url_for('login'))
    
    return render_template("page_3_RegisterPage.html", form=form)

# Page 4 - Dashboard Page
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("page_4_dashboardPage.html")

# Page 5 - Appointments Manager Page
@app.route("/appointments")
@login_required
def appointments():
    return render_template("page_5_AppointmentsManagerPage.html")

# Page 6 - Add Appointment Page
@app.route("/appointments/add_appointment")
@login_required
def add_appointment():
    return render_template("page_6_AddAppointmentPage.html")

# Page 7 - Calendar View Page
@app.route("/calender")
@login_required
def calender():
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
@app.route("/user_Profile")
@login_required
def user_Profile():
    return render_template("page_11_UserProfileSettingsPage.html")

# Page 12 - Edit Appointment Page
@app.route("/appointments/edit_appointment")
@login_required
def edit_appointment():
    return render_template("page_12_EditAppointmentPage.html")

# Page 13 - Edit Document Page
@app.route("/medical_document/edit_document")
@login_required
def edit_document():
    return render_template("page_13_EditDocumentPage.html")