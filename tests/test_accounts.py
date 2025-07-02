from financeapp.accounts.models import User


def test_profile_get(client, auth):
    auth.login()
    response = client.get("/profile/")
    assert response.status_code == 200
    assert b"profile" in response.data


def test_profile_requires_login(client):
    response = client.get("/profile/", follow_redirects=True)
    assert response.status_code == 200
    assert b"login" in response.data


def test_confirmed_user_can_login(app, client):
    response = client.post("/accounts/login", data={
        "email": "test@test.com",
        "password": "password"
    }, follow_redirects=True)
    response.status_code == 302
    assert b"Welcome" in response.data


def test_unconfirmed_user_cannot_login(app, client):
    response = client.post("/accounts/login", data={
        "email": "unconfirmed@test.com",
        "password": "password"
    }, follow_redirects=True)
    assert b"Email requires confirmation" in response.data


def test_register_success(client, db_session):
    response = client.post('/accounts/register', data={
        'email': 'user@test.com',
        'password': 'password',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert (b'please click on the link in the email'
            in response.data)

    user = User.query.filter_by(email='user@test.com').first()
    assert user is not None
    assert user.confirmed_at is None


def test_register_missing_email(client):
    response = client.post('/accounts/register', data={
        'email': '',
        'password': 'password',
    }, follow_redirects=True)
    assert b'Email not provided' in response.data
    assert response.status_code == 200


def test_register_missing_password(client):
    response = client.post('/accounts/register', data={
        'email': 'auser@test.com',
        'password': '',
    }, follow_redirects=True)
    assert b'Password not provided' in response.data
    assert response.status_code == 200


def test_register_duplicate_email(client, db_session):
    response = client.post('/accounts/register', data={
        'email': 'test@test.com',
        'password': 'password',
    }, follow_redirects=True)

    assert b'is already associated with an account' in response.data
    assert response.status_code == 200
