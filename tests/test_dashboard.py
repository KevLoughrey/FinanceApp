def test_dashboard_requires_login(client):
    response = client.get("/finances/dashboard",  follow_redirects=True)
    assert b"login" in response.data


def test_dashboard_get(client, auth):
    auth.login()
    response = client.get("/finances/dashboard")
    assert response.status_code == 200
    assert b"dashboard" in response.data
