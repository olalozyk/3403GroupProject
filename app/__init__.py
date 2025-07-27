import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_socketio import SocketIO
from dotenv import load_dotenv
from app.config import DeploymentConfig

# Load environment variables from a .env file (locally)
load_dotenv()

# Flask extensions (uninitialized)
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login = LoginManager()
socketio = SocketIO(cors_allowed_origins="*")


def create_app(config=DeploymentConfig):
    app = Flask(__name__, instance_relative_config=True)

    # Load config object (default is DeploymentConfig for Heroku)
    app.config.from_object(config)

    # Register blueprints (adjust import paths as needed)
    from app.blueprints import blueprint
    app.register_blueprint(blueprint)

    # Initialize Flask extensions with app context
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login.init_app(app)
    login.login_view = 'main.login'
    socketio.init_app(app)

    # Import models/routes/sockets after app is created
    from app import routes, models, sockets

    return app
