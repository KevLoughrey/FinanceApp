from financeapp.run import create_app


def test_create_app_with_default_config(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "secret")
    monkeypatch.setenv("DATABASE_URI", "sqlite:///:memory:")

    app = create_app()
    assert app.config["SECRET_KEY"] == "secret"
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
