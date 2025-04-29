import os
from flask import Flask
from app.extensions import db, migrate, csrf, socketio, login_manager
from dotenv import load_dotenv
load_dotenv()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')  # fallback to 'dev' key if missing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'project.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # recommended to turn off

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app