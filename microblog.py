from flask_migrate import Migrate
from app import socketio, create_app,db
from app.config import DeploymentConfig

if __name__ == '__main__':
    application = create_app(DeploymentConfig)
    migrate = Migrate(application,db)
    socketio.run(application, debug=True)

