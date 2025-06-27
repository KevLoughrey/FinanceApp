import os
from dotenv import load_dotenv
from flask import Flask
from financeapp.database import db
from flask_security import Security
from financeapp.home import home_bp
from financeapp.accounts import profiles_bp
from financeapp.accounts import user_datastore
from financeapp.accounts.utils import init_db as init_accounts_db
from financeapp.finances import finances_bp
from financeapp.finances.utils import init_db as init_finances_db
from flask_mailman import Mail
from flask_bootstrap import Bootstrap5

load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is not None:
        app.config.update(test_config)
    else:
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

    if test_config is None:
        with app.app_context():
            db.create_all()
            init_accounts_db()
            init_finances_db()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
