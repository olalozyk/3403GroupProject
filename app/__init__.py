from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from app.config import Config
from dotenv import load_dotenv
from flask_login import LoginManager
import os

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')

# Set up extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# Configure login manager
login = LoginManager()
login.init_app(app)
login.login_view = 'login'

from app import routes, models

