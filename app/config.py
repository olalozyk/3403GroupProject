import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance')),
        'ChronicCare.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
