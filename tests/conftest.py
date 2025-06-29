import pytest
import uuid
from financeapp.run import create_app
from financeapp.database import db
from financeapp.accounts.models import User
from financeapp.finances.models import ExpenseCategory
from flask_security.utils import hash_password
from datetime import datetime


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECURITY_PASSWORD_SALT": "test_salt",
        "MAIL_SUPPRESS_SEND": True,
        "SECRET_KEY": "secret",
        "SECURITY_URL_PREFIX": "/accounts",
        "SECURITY_BLUEPRINT_NAME": "accounts",
        "SECURITY_REGISTERABLE": True,
        "SECURITY_CONFIRMABLE": True,
        "SECURITY_SEND_REGISTER_EMAIL": False,
        "MAIL_SUPPRESS_SEND": True,
    })

    with app.app_context():
        db.create_all()

        user = User(email="test@test.com",
                    password=hash_password("password"),
                    active=True,
                    fs_uniquifier=str(uuid.uuid4()),
                    confirmed_at=datetime.now(),)
        db.session.add(user)

        unconfirmed_user = User(
            email="unconfirmed@test.com",
            password=hash_password("password"),
            fs_uniquifier=str(uuid.uuid4()),
            active=True,
            confirmed_at=None,
        )
        db.session.add(unconfirmed_user)
        
        db.session.commit()

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email='test@test.com', password='password'):
        return self._client.post(
            '/accounts/login',
            data={'email': email, 'password': password},
            follow_redirects=True,
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session


@pytest.fixture
def category(app):
    with app.app_context():
        category = ExpenseCategory(name="Test Category")
        db.session.add(category)
        db.session.commit()
        category_id = category.id
    return category_id
