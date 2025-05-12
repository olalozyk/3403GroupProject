from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_socketio import SocketIO
from app.config import Config
from dotenv import load_dotenv
import os

load_dotenv()

# Create core app and extensions
app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login = LoginManager()
socketio = SocketIO(cors_allowed_origins="*")

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)
csrf.init_app(app)
login.init_app(app)
login.login_view = 'index'
socketio.init_app(app)

# Import routes *after* app and extensions are set up
with app.app_context():
    from app import routes, models, sockets  # Ensure sockets.py exists

