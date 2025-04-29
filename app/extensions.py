from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_socketio import SocketIO

# Create extension instances (not tied to app yet)
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
socketio = SocketIO()
login_manager = LoginManager()
login_manager.login_view = 'login'  # Redirect here if login required
login_manager.login_message_category = "info"