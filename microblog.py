from dotenv import load_dotenv
import os
load_dotenv()

from flask_migrate import Migrate
from app import socketio, create_app, db
from app.config import ProductionConfig  # instead of DeploymentConfig


# Make these available globally for Flask CLI
application = create_app(ProductionConfig)
migrate = Migrate(application, db)

# Run with SocketIO if script is executed directly
if __name__ == '__main__':
    import eventlet
    import eventlet.wsgi
    eventlet.monkey_patch()

    socketio.run(application, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))


