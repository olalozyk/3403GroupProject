import os
import sys
import pytest
from flask import session

# Add parent directory to path so 'app' module can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from app
from app import db, create_app
from app.models import User

@pytest.fixture
def app():
    """Create a Flask app for testing authentication"""
    # Create the Flask app instance with test configuration
    app = create_app()
    
    # Configure the Flask app for testing
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-key',
    })
    
    # Create app context and set up database
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create a test user"""
    with app.app_context():
        user = User(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            role='member'
        )
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        return user.id

def test_login_page_loads(client):
    """Test that the login page loads correctly"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_user_password_hashing(app):
    """Test that passwords are properly hashed and verified"""
    with app.app_context():
        user = User(
            first_name='Hash',
            last_name='Test',
            email='hash@example.com'
        )
        
        user.set_password('testpassword')
        assert user.password != 'testpassword'  
        assert len(user.password) > 20
        
        # Password verification
        assert user.check_password('testpassword') is True
        assert user.check_password('wrongpassword') is False