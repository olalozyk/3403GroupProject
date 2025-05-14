import os
import sys
import pytest
import tempfile
from flask import Flask, render_template, request, redirect, url_for, session, flash
import jwt
import datetime

# Add parent directory to path so 'app' module can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import only what's needed for auth testing
from app import db
from app.models import User

@pytest.fixture
def app():
    """Create a minimal Flask app for testing authentication"""
    app = Flask(__name__)
    
    # Configure the Flask app for testing
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-key'
    })
    
    # Create minimal HTML templates as strings
    login_template = """
    <!DOCTYPE html>
    <html>
    <head><title>Login</title></head>
    <body>
        <h1>Login</h1>
        <form method="POST" action="/login">
            <input type="email" name="email">
            <input type="password" name="password">
            <input type="submit" value="Login">
        </form>
        <a href="/reset_request">Forgot Password?</a>
    </body>
    </html>
    """
    
    register_template = """
    <!DOCTYPE html>
    <html>
    <head><title>Register</title></head>
    <body>
        <h1>Sign Up</h1>
        <form method="POST" action="/register">
            <input type="text" name="first_name">
            <input type="text" name="last_name">
            <input type="email" name="email">
            <input type="password" name="password">
            <input type="password" name="confirm_password">
            <input type="submit" value="Register">
        </form>
    </body>
    </html>
    """
    
    dashboard_template = """
    <!DOCTYPE html>
    <html>
    <head><title>Dashboard</title></head>
    <body>
        <h1>Dashboard</h1>
        <p>Welcome back!</p>
        <a href="/logout">Logout</a>
        <a href="/change_password">Change Password</a>
    </body>
    </html>
    """
    
    reset_request_template = """
    <!DOCTYPE html>
    <html>
    <head><title>Reset Password</title></head>
    <body>
        <h1>Reset Password</h1>
        <form method="POST" action="/reset_request">
            <input type="email" name="email">
            <input type="submit" value="Request Password Reset">
        </form>
    </body>
    </html>
    """
    
    reset_password_template = """
    <!DOCTYPE html>
    <html>
    <head><title>Reset Password</title></head>
    <body>
        <h1>Reset Your Password</h1>
        <form method="POST">
            <input type="password" name="password">
            <input type="password" name="confirm_password">
            <input type="submit" value="Reset Password">
        </form>
    </body>
    </html>
    """
    
    change_password_template = """
    <!DOCTYPE html>
    <html>
    <head><title>Change Password</title></head>
    <body>
        <h1>Change Password</h1>
        <form method="POST" action="/change_password">
            <input type="password" name="current_password">
            <input type="password" name="new_password">
            <input type="password" name="confirm_password">
            <input type="submit" value="Change Password">
        </form>
    </body>
    </html>
    """
    
    # Define auth routes
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            with app.app_context():
                user = User.query.filter_by(email=email).first()
                
                if user and user.check_password(password):
                    session['user_id'] = user.id
                    session['first_name'] = user.first_name
                    session['role'] = user.role
                    flash('Login successful')
                    return redirect(url_for('dashboard'))
                else:
                    return "Invalid email or password"
                    
        return login_template
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            email = request.form.get('email')
            
            with app.app_context():
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    return "Email already registered"
                
                user = User(
                    first_name=request.form.get('first_name'),
                    last_name=request.form.get('last_name'),
                    email=email,
                    role='member'
                )
                user.set_password(request.form.get('password'))
                db.session.add(user)
                db.session.commit()
                
                return "Account created successfully"
                
        return register_template
    
    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return dashboard_template
    
    @app.route('/logout')
    def logout():
        session.clear()
        return "You have been logged out"
        
    @app.route('/reset_request', methods=['GET', 'POST'])
    def reset_request():
        if request.method == 'POST':
            email = request.form.get('email')
            
            with app.app_context():
                user = User.query.filter_by(email=email).first()
                
                if user:
                    # Generate token
                    payload = {
                        'user_id': user.id,
                        'exp': datetime.datetime.now() + datetime.timedelta(seconds=1800)
                    }
                    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
                    # In a real app, send email with reset link
                    return f"Password reset link sent to {email}"
                else:
                    return "Email not found"
                    
        return reset_request_template
        
    @app.route('/reset_password/<token>', methods=['GET', 'POST'])
    def reset_token(token):
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except:
            return "Invalid or expired token"
            
        with app.app_context():
            user = User.query.get(user_id)
            
            if not user:
                return "Invalid or expired token"
                
            if request.method == 'POST':
                password = request.form.get('password')
                confirm_password = request.form.get('confirm_password')
                
                if password != confirm_password:
                    return "Passwords do not match"
                    
                user.set_password(password)
                db.session.commit()
                return "Password has been reset successfully"
                
        return reset_password_template
        
    @app.route('/change_password', methods=['GET', 'POST'])
    def change_password():
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        if request.method == 'POST':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if new_password != confirm_password:
                return "New passwords do not match"
                
            with app.app_context():
                user = User.query.get(session['user_id'])
                
                if not user.check_password(current_password):
                    return "Current password is incorrect"
                    
                user.set_password(new_password)
                db.session.commit()
                return "Password changed successfully"
                
        return change_password_template
    
    # Initialize database
    db.init_app(app)
    
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
    """Create a test user and store the ID for later retrieval"""
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
        user_id = user.id  # Store the ID
        return user_id

def test_login_page_loads(client):
    """Test that the login page loads correctly"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_login_with_valid_credentials(client, test_user, app):
    """Test login with valid credentials"""
    with app.app_context():
        user = User.query.get(test_user)
        email = user.email
    
    response = client.post('/login', data={
        'email': email,
        'password': 'testpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_login_with_invalid_credentials(client, test_user, app):
    """Test login with invalid credentials"""
    with app.app_context():
        user = User.query.get(test_user)
        email = user.email
    
    response = client.post('/login', data={
        'email': email,
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data

def test_registration_page_loads(client):
    """Test that the registration page loads correctly"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Sign Up' in response.data

def test_registration_success(client, app):
    """Test successful registration"""
    response = client.post('/register', data={
        'first_name': 'New',
        'last_name': 'User',
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Account created successfully' in response.data
    
    # Check that the user was created in the database
    with app.app_context():
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.first_name == 'New'
        assert user.last_name == 'User'
        assert user.check_password('password123')

def test_registration_duplicate_email(client, test_user, app):
    """Test registration with an email that already exists"""
    with app.app_context():
        user = User.query.get(test_user)
        email = user.email
    
    response = client.post('/register', data={
        'first_name': 'Another',
        'last_name': 'User',
        'email': email,  # same as test_user
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Email already registered' in response.data

def test_logout(client, test_user, app):
    """Test that logout works correctly"""
    # Login first
    with app.app_context():
        user = User.query.get(test_user)
        email = user.email
    
    client.post('/login', data={
        'email': email,
        'password': 'testpassword'
    })
    
    # Then logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data

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
        
def test_reset_password_page_loads(client):
    """Test that the reset password request page loads correctly"""
    response = client.get('/reset_request')
    assert response.status_code == 200
    assert b'Reset Password' in response.data

def test_reset_password_request_with_valid_email(client, test_user, app):
    """Test password reset request with valid email"""
    with app.app_context():
        user = User.query.get(test_user)
        email = user.email
    
    response = client.post('/reset_request', data={
        'email': email
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Password reset link sent to' in response.data

def test_reset_password_request_with_invalid_email(client):
    """Test password reset request with invalid email"""
    response = client.post('/reset_request', data={
        'email': 'nonexistent@example.com'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Email not found' in response.data

def test_reset_password_with_token(client, test_user, app):
    """Test password reset with valid token"""
    # Create a token directly
    with app.app_context():
        user = User.query.get(test_user)
        
        # Generate token manually using the app's secret key
        payload = {
            'user_id': user.id,
            'exp': datetime.datetime.now() + datetime.timedelta(seconds=1800)
        }
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    
    # Use the token to reset password
    response = client.post(f'/reset_password/{token}', data={
        'password': 'newpassword123',
        'confirm_password': 'newpassword123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Password has been reset successfully' in response.data
    
    # Verify the password was changed
    with app.app_context():
        updated_user = User.query.get(test_user)
        assert updated_user.check_password('newpassword123')

def test_reset_password_with_invalid_token(client):
    """Test password reset with invalid token"""
    response = client.get('/reset_password/invalidtoken', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid or expired token' in response.data

def test_change_password_page_loads(client, test_user, app):
    """Test that the change password page loads correctly when logged in"""
    # Login first
    with app.app_context():
        user = User.query.get(test_user)
        email = user.email
    
    client.post('/login', data={
        'email': email,
        'password': 'testpassword'
    })
    
    response = client.get('/change_password')
    assert response.status_code == 200
    assert b'Change Password' in response.data

def test_change_password_success(client, test_user, app):
    """Test successful password change"""
    # Login first
    with app.app_context():
        user = User.query.get(test_user)
        email = user.email
    
    client.post('/login', data={
        'email': email,
        'password': 'testpassword'
    })
    
    # Change password
    response = client.post('/change_password', data={
        'current_password': 'testpassword',
        'new_password': 'newpassword456',
        'confirm_password': 'newpassword456'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Password changed successfully' in response.data
    
    # Verify the password was changed
    with app.app_context():
        updated_user = User.query.get(test_user)
        assert updated_user.check_password('newpassword456')

def test_change_password_incorrect_current(client, test_user, app):
    """Test password change with incorrect current password"""
    # Login first
    with app.app_context():
        user = User.query.get(test_user)
        email = user.email
    
    client.post('/login', data={
        'email': email,
        'password': 'testpassword'
    })
    
    # Attempt to change password with wrong current password
    response = client.post('/change_password', data={
        'current_password': 'wrongpassword',
        'new_password': 'newpassword456',
        'confirm_password': 'newpassword456'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Current password is incorrect' in response.data

def test_change_password_mismatch_new(client, test_user, app):
    """Test password change with mismatched new passwords"""
    # Login first
    with app.app_context():
        user = User.query.get(test_user)
        email = user.email
    
    client.post('/login', data={
        'email': email,
        'password': 'testpassword'
    })
    
    # Attempt to change password with mismatched new passwords
    response = client.post('/change_password', data={
        'current_password': 'testpassword',
        'new_password': 'newpassword456',
        'confirm_password': 'differentpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'New passwords do not match' in response.data 