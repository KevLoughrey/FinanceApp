import os
from database import db
from dotenv import load_dotenv
from flask import Flask
from flask_security import Security
from home import home_bp
from accounts import ExtendedRegistrationForm, user_datastore
from accounts.utils import init_db as init_accounts_db

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SALT')

    app.config['SECURITY_REGISTERABLE'] = True
    app.config['SECURITY_RECOVERABLE'] = True
    app.config['SECURITY_CHANGEABLE'] = True

    app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = [
        {"email": {"lookup": "iexact"}},
        {"username": {"lookup": "iexact"}}
    ]
    app.config['SECURITY_REGISTER_FORM'] = ExtendedRegistrationForm

    app.config['SECURITY_URL_PREFIX'] = '/accounts'
    app.config['SECURITY_BLUEPRINT_NAME'] = 'accounts'

    app.register_blueprint(home_bp, url_prefix='')

    db.init_app(app)
    security = Security(app, user_datastore)

    with app.app_context():
        init_accounts_db()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
