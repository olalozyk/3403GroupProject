from app.models import User, Appointment, Document, UserProfile

def test_user_password():
    user = User(first_name='Test', last_name='User', email='user@example.com')
    user.set_password('secret')
    assert user.check_password('secret')

def test_appointment_creation():
    appt = Appointment(
        user_id=1,
        practitioner_type='GP',
        practitioner_name='Dr. Smith',
        appointment_date='2025-01-01',
        starting_time='10:00',
        ending_time='10:30',
        location='Clinic',
        appointment_type='Checkup',
        appointment_notes='Bring reports'
    )
    assert appt.practitioner_name == 'Dr. Smith'

def test_document_creation():
    doc = Document(
        user_id=1,
        file='report.pdf',
        document_name='Test Report',
        upload_date='2025-01-01',
        document_type='Lab',
        document_notes='Blood test',
        practitioner_name='Dr. Adams'
    )
    assert doc.document_name == 'Test Report'

def test_userprofile_creation():
    profile = UserProfile(
        user_id=1,
        mobile_number='0400123456',
        date_of_birth='1990-01-01',
        address='123 Test St',
        gender='Male',
        insurance_type='Private'
    )
    assert profile.mobile_number == '0400123456'
    assert profile.gender == 'Male'
