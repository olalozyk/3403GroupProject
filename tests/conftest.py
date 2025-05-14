import os
import sys
import pytest
from flask import template_rendered
from contextlib import contextmanager

# Add parent directory to path so 'app' module can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the application module
from app import create_app, db
from app.models import User

@contextmanager
def captured_templates(app):
    """Context manager for capturing templates rendered during a request."""
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

@pytest.fixture(scope='function')
def app():
    """Create a Flask app for testing"""
    # Create the Flask app instance with test configuration
    flask_app = create_app()
    
    # Configure app for testing
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SERVER_NAME': 'localhost'
    })
    
    # Create app context for the test
    with flask_app.app_context():
        # Create database tables
        db.create_all()
        
        # Yield the app for testing
        yield flask_app
        
        # Clean up after tests
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Create a test client"""
    with app.test_client() as client:
        # Set up application context for the client
        with app.app_context():
            # Enable session in the client
            with client.session_transaction() as sess:
                sess['_fresh'] = True  # Mark session as fresh
            yield client

@pytest.fixture(scope='function')
def test_user(app):
    """Create a test user"""
    with app.app_context():
        # Check if user already exists
        user = User.query.filter_by(email='test@example.com').first()
        
        # Create user if not exists
        if not user:
            user = User(
                first_name='Test',
                last_name='User',
                email='test@example.com',
                role='member'
            )
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()
        
        return user

@pytest.fixture(scope='function')
def login_test_user(client, test_user):
    """Fixture to log in a test user"""
    def _login():
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['first_name'] = test_user.first_name
            sess['role'] = test_user.role
    
    return _login

@pytest.fixture(scope='function')
def authenticated_client(app, client, test_user):
    """Create a client that is already logged in"""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id
        sess['first_name'] = test_user.first_name
        sess['role'] = test_user.role
    
    return client