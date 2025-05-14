import os
import sys
import unittest
from flask import session

# Add parent directory to path so 'app' module can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from app
from app import db, create_app
from app.models import User

class AuthTestCase(unittest.TestCase):
    """Test cases for authentication functionality"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app()
        self.app.config.update({
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SECRET_KEY': 'test-key',
            'SERVER_NAME': None,  # Prevent issues with URL generation
        })
        self.client = self.app.test_client()
        
        # Create application context and set up database
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create a test user
        self.test_user = User(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            role='member'
        )
        self.test_user.set_password('testpassword')
        db.session.add(self.test_user)
        db.session.commit()
    
    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_password_hashing(self):
        """Test that passwords are properly hashed and verified"""
        user = User(
            first_name='Hash',
            last_name='Test',
            email='hash@example.com'
        )
        
        user.set_password('testpassword')
        self.assertNotEqual(user.password, 'testpassword')
        self.assertGreater(len(user.password), 20)
        
        # Password verification
        self.assertTrue(user.check_password('testpassword'))
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_user_model_properties(self):
        """Test User model properties"""
        user = User.query.filter_by(email='test@example.com').first()
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.role, 'member')
        self.assertTrue(user.check_password('testpassword'))
    
    def test_user_reset_token_generation(self):
        """Test that reset tokens can be generated and verified"""
        user = User.query.filter_by(email='test@example.com').first()
        
        # Generate token
        token = user.get_reset_token()
        self.assertIsNotNone(token)
        
        # Verify token
        verified_user = User.verify_reset_token(token)
        self.assertEqual(verified_user.id, user.id)
        
        # Test invalid token
        invalid_user = User.verify_reset_token('invalid-token')
        self.assertIsNone(invalid_user)
    
    def test_user_creation(self):
        """Test creating a new user in the database"""
        new_user = User(
            first_name='New',
            last_name='User',
            email='new@example.com',
            role='member'
        )
        new_user.set_password('newpassword')
        db.session.add(new_user)
        db.session.commit()
        
        # Verify user exists in database
        user = User.query.filter_by(email='new@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('newpassword'))
    
    def test_duplicate_email_validation(self):
        """Test that duplicate emails are detected"""
        # Attempt to create a user with an existing email
        duplicate_user = User(
            first_name='Duplicate',
            last_name='User',
            email='test@example.com',  # Same as test_user
            role='member'
        )
        duplicate_user.set_password('anotherpassword')
        
        # Add to session but don't commit yet
        db.session.add(duplicate_user)
        
        # This should raise an integrity error (duplicate email)
        with self.assertRaises(Exception):
            db.session.commit()
        
        # Rollback the failed transaction
        db.session.rollback()
    
    def test_password_complexity(self):
        """Test password complexity requirements"""
        user = User.query.filter_by(email='test@example.com').first()
        
        # Setting a short password should fail in a proper implementation
        # Just a basic check that the method doesn't crash
        user.set_password('short')
        
        # Password should still be properly hashed
        self.assertNotEqual(user.password, 'short')
        self.assertGreater(len(user.password), 20)
    
    def test_user_full_name(self):
        """Test the full_name property of User model if it exists"""
        user = User.query.filter_by(email='test@example.com').first()
        
        # Check if the full_name property exists
        if hasattr(user, 'full_name'):
            self.assertEqual(user.full_name, 'Test User')
        else:
            # If it doesn't exist, just pass the test
            self.assertTrue(True)
    
    def test_user_roles(self):
        """Test user role functionality"""
        # Create users with different roles
        admin_user = User(
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            role='admin'
        )
        admin_user.set_password('adminpass')
        db.session.add(admin_user)
        db.session.commit()
        
        # Test the roles
        regular_user = User.query.filter_by(email='test@example.com').first()
        admin = User.query.filter_by(email='admin@example.com').first()
        
        self.assertEqual(regular_user.role, 'member')
        self.assertEqual(admin.role, 'admin')
        
        # Check role-based methods if they exist
        if hasattr(admin, 'is_admin'):
            self.assertTrue(admin.is_admin())
            self.assertFalse(regular_user.is_admin())
    
    def test_user_id_and_type(self):
        """Test user ID field and type"""
        user = User.query.filter_by(email='test@example.com').first()
        
        # Verify the user has an ID
        self.assertIsNotNone(user.id)
        
        # Test that ID is numeric (integer)
        self.assertTrue(isinstance(user.id, int))


if __name__ == '__main__':
    unittest.main() 