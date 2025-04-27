from flask import render_template

from app import app

@app.route('/')

@app.route('/index')
def index():
    return render_template("page_1_LandingPage.html")

@app.route("/login")
def login():
    return render_template("page_2_loginPage.html")

@app.route("/register")
def register():
    return render_template("page_3_registerPage.html")

@app.route("/dashboard")
def dashboard():
    return render_template("page_4_dashboardPage.html")

@app.route("/appointments")
def appointments():
    return render_template("page_5_AppointmentsManagerPage.html")

@app.route("/appointments/add_appointment")
def add_appointment():
    return render_template("page_6_AddAppointmentPage.html")

@app.route("/appointments/edit_appointment")
def edit_appointment():
    return render_template("page_12_EditAppointmentPage.html")

@app.route("/calender")
def calender():
    return render_template("page_7_CalendarViewPage.html")

@app.route("/medical_document")
def medical_document():
    return render_template("page_8_MedicalDocumentsManagerPage.html")

@app.route("/medical_document/upload_document")
def upload_document():
    return render_template("page_9_UploadNewDocumentPage.html")

@app.route("/medical_document/edit_document")
def edit_document():
    return render_template("page_12_EditDocumentPage.html")

@app.route("/medical_document/share_document")
def share_document():
    return render_template("page_10_SelectDocumentsToSharePage.html")

@app.route("/user_Profile")
def user_Profile():
    return render_template("page_11_UserProfileSettingsPage.html")

