from app.models import User, Appointment, Document, UserProfile

def test_user_password():
    user = User()
    user.set_password('test123')
    assert user.password != 'test123'
    assert user.check_password('test123') is True

def test_appointment_creation():
    appt = Appointment(appointment_type='consultation')
    assert appt.appointment_type == 'consultation'

def test_document_creation():
    doc = Document(document_name='Report A')
    assert doc.document_name == 'Report A'

def test_userprofile_creation():
    profile = UserProfile(
        user_id=1,
        mobile_number='0400123456',
        email='testprofile@example.com',
        password='testpassword'
    )
    assert profile.email == 'testprofile@example.com'
    assert profile.mobile_number.startswith('0400')
