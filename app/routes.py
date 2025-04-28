from flask import render_template

from app import app

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
