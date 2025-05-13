from app import socketio, create_app

if __name__ == '__main__':
    socketio.run(app, debug=True)

