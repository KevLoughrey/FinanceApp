import os
from database import db
from dotenv import load_dotenv
from flask import Flask
from flask_security import Security
from home import home_bp
from accounts import profiles_bp
from accounts import user_datastore
from accounts.utils import init_db as init_accounts_db
from finances import finances_bp
from finances.utils import init_db as init_finances_db
from flask_mailman import Mail
from flask_bootstrap import Bootstrap5

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

    app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SALT')
    app.config['SECURITY_REGISTERABLE'] = True
    app.config['SECURITY_RECOVERABLE'] = True
    app.config['SECURITY_CHANGEABLE'] = True
    app.config["SECURITY_CONFIRMABLE"] = True
    app.config['SECURITY_URL_PREFIX'] = '/accounts'
    app.config['SECURITY_BLUEPRINT_NAME'] = 'accounts'

    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
    app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

    app.register_blueprint(home_bp, url_prefix='')
    app.register_blueprint(profiles_bp, url_prefix='/profile')
    app.register_blueprint(finances_bp, url_prefix='/finances')

    db.init_app(app)
    mail = Mail(app) # noqa
    security = Security(app, user_datastore) # noqa
    Bootstrap5(app)

    with app.app_context():
        db.create_all()
        init_accounts_db()
        init_finances_db()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
