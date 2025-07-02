def test_dashboard_requires_login(client):
    response = client.get("/finances/my_finances",  follow_redirects=True)
    assert b"login" in response.data


def test_dashboard_get(client, auth):
    auth.login()
    response = client.get("/finances/my_finances")
    assert response.status_code == 200
    assert b"my_finances" in response.data
