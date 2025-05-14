import sys
import os
import unittest
import warnings

from app import create_app, db
from app.models import User, Appointment
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Suppress noisy test resource warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

class AppointmentTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()  # ✅ Ensure tables are created

            user = User.query.filter_by(email="test@example.com").first()
            if not user:
                user = User(
                    first_name="Test",
                    last_name="User",
                    email="test@example.com",
                    password=generate_password_hash("yourpassword"),
                    role="member"
                )
                db.session.add(user)
                db.session.commit()

            self.test_user_id = user.id

    def login_session(self):
        return self.client.post("/login", data={
            "email": "test@example.com",
            "password": "yourpassword"
        }, follow_redirects=True)

    def test_add_appointment(self):
        self.login_session()

        today = datetime.today().date()
        tomorrow = today + timedelta(days=1)

        response = self.client.post("/appointment/add", data={
            "appointment_date": today.strftime('%Y-%m-%d'),
            "starting_time": "09:00",
            "ending_time": "10:00",
            "practitioner_name": "Dr. Smith",
            "practitioner_type": "General Practitioner (GP)",
            "location": "Test Clinic",
            "provider_number": "123456",
            "appointment_type": "General",
            "appointment_notes": "Unittest appointment.",
            "reminder": ["2 hours before", "1 day before"],
            "custom_reminder": tomorrow.strftime('%Y-%m-%d')
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Appointment successfully created", response.data)

        with self.app.app_context():
            appt = Appointment.query.filter_by(practitioner_name="Dr. Smith").first()
            self.assertIsNotNone(appt)
            self.assertEqual(appt.location, "Test Clinic")
            self.assertEqual(appt.reminder, "2 hours before,1 day before")
            self.assertEqual(appt.custom_reminder, tomorrow)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

if __name__ == "__main__":
    unittest.main()
