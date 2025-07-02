from financeapp.finances.models import IncomeCategory, Income
from financeapp.accounts.models import User
from financeapp.finances.utils import init_db
from datetime import date
from decimal import Decimal
import json


def create_income(db_session, user, income_category):
    income = Income(
        name="Salary",
        date=date(2025, 6, 1),
        description="June salary payment",
        amount=Decimal("3000.00"),
        user_id=user.id,
        category_id=income_category
    )
    print(income_category)
    db_session.add(income)
    db_session.commit()
    return income


def test_db_create_income_category(db_session):
    category = IncomeCategory(name="Benefits")
    db_session.add(category)
    db_session.commit()

    assert category.id is not None
    assert str(category) == "Benefits"


def test_db_create_income(db_session, income_category):
    user = User.query.filter_by(email="test@test.com").first()
    income = create_income(db_session, user, income_category)
    print(income)
    assert income.id is not None
    assert income.name == "Salary"
    assert income.amount == Decimal("3000.00")
    assert income.user == user
    assert income.category.name == "Salary"


def test_finance_init_db_creates_default_categories(app, db_session):
    with app.app_context():
        init_db()
        categories = [cat.name for cat in IncomeCategory.query.all()]
        assert set(categories) == {'Salary', 'Freelance', 'Savings',
                                   'Benefits', 'Gifts', 'Other'}


def test_finance_init_db_does_not_duplicate(app, db_session):
    with app.app_context():
        db_session.add(IncomeCategory(name='Salary'))
        db_session.commit()

        init_db()

        count = IncomeCategory.query.filter_by(name='Salary').count()
        assert count == 1


def test_add_income_requires_login(client, auth):
    response = client.get("/finances/add_income", follow_redirects=True)
    assert b"login" in response.data


def test_add_income_get(client, auth):
    auth.login()
    response = client.get("/finances/add_income")
    assert response.status_code == 200
    assert b"Add Income" in response.data


def test_add_income_success(client, auth, app, income_category):
    auth.login()
    response = client.post("/finances/add_income", data={
        "name": "Test Income",
        "date": "2025-01-01",
        "description": "Test description",
        "amount": "123.45",
        "category": income_category,
    }, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        income = Income.query.filter_by(name="Test Income").first()
        assert income is not None
        assert float(income.amount) == 123.45


def test_add_income_missing_required_fields(client, auth):
    auth.login()
    response = client.post("/finances/add_income", data={},
                           follow_redirects=True)
    assert response.status_code == 200
    assert response.data.count(b"This field is required") >= 3


def test_add_income_negative_amount(client, auth, income_category):
    auth.login()
    response = client.post("/finances/add_income", data={
        "name": "Test Income",
        "date": "2025-01-01",
        "description": "Test description",
        "amount": "-50.00",
        "category": income_category,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Amount must be a positive number" in response.data


def test_add_income_invalid_date_format(client, auth, income_category):
    auth.login()
    response = client.post("/finances/add_income", data={
        "name": "Test Income",
        "date": "lorem",
        "description": "Test description",
        "amount": "123.45",
        "category": income_category,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"This field is required" in response.data


def test_add_income_invalid_category(client, auth):
    auth.login()
    response = client.post("/finances/add_income", data={
        "name": "Test Income",
        "date": "2025-01-01",
        "description": "Test description",
        "amount": "123.45",
        "category": 1000,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Not a valid choice" in response.data


def test_add_income_amount_not_a_number(client, auth, income_category):
    auth.login()
    response = client.post("/finances/add_income", data={
        "name": "Test Income",
        "date": "2025-01-01",
        "description": "Test description",
        "amount": "lorem",
        "category": income_category,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"This field is required" in response.data


def test_edit_income_success(client, auth, db_session, income_category):
    auth.login()
    user = User.query.filter_by(email="test@test.com").first()
    income = create_income(db_session, user, income_category)

    data = {
        "name": "Updated Name",
        "date": "1999-07-01",
        "description": "Updated description",
        "amount": 999.99,
        "category": income_category,
    }
    response = client.patch(f"/finances/edit_income/{income.id}",
                            data=json.dumps(data),
                            content_type="application/json")

    assert response.status_code == 200
    result = response.get_json()
    assert result["success"]
    assert result["income"]["name"] == "Updated Name"
    assert result["income"]["description"] == "Updated description"
    assert result["income"]["date"] == "1999-07-01"
    assert result["income"]["amount"] == "999.99"
    assert result["income"]["category_id"] == 1


def test_edit_income_invalid_category(client, auth, db_session,
                                      income_category):
    auth.login()
    user = User.query.filter_by(email="test@test.com").first()
    income = create_income(db_session, user, income_category)

    data = {
        "name": "Bad Category",
        "date": "2025-07-01",
        "description": "Invalid category",
        "amount": 50.00,
        "category": 1000,
    }
    response = client.patch(f"/finances/edit_income/{income.id}",
                            data=json.dumps(data),
                            content_type="application/json")

    assert not response.get_json()["success"]
    assert "category" in response.get_json()["errors"]


def test_edit_income_negative_amount(client, auth, db_session,
                                     income_category):
    auth.login()
    user = User.query.filter_by(email="test@test.com").first()
    income = create_income(db_session, user, income_category)

    data = {
        "name": "Bad Amount",
        "date": "2025-07-01",
        "description": "Negative",
        "amount": -50.00,
        "category": income_category,
    }
    response = client.patch(f"/finances/edit_income/{income.id}",
                            data=json.dumps(data),
                            content_type="application/json")

    assert not response.get_json()["success"]
    assert "amount" in response.get_json()["errors"]


def test_edit_income_invalid_date(client, auth, db_session, income_category):
    auth.login()
    user = User.query.filter_by(email="test@test.com").first()
    income = create_income(db_session, user, income_category)

    data = {
        "name": "Bad Date",
        "date": "not-a-date",
        "description": "error",
        "amount": 10.00,
        "category": income_category,
    }
    response = client.patch(f"/finances/edit_income/{income.id}",
                            data=json.dumps(data),
                            content_type="application/json")

    assert not response.get_json()["success"]
    assert "date" in response.get_json()["errors"]


def test_edit_income_missing_fields(client, auth, db_session,
                                    income_category):
    auth.login()
    user = User.query.filter_by(email="test@test.com").first()
    income = create_income(db_session, user, income_category)

    response = client.patch(f"/finances/edit_income/{income.id}",
                            data=json.dumps({}),
                            content_type="application/json")

    assert not response.get_json()["success"]
    assert "name" in response.get_json()["errors"]
    assert "date" in response.get_json()["errors"]


def test_edit_income_other_user_forbidden(client, auth,
                                          db_session, income_category):
    auth.login()
    other_user = User.query.filter_by(email="second@test.com").first()
    income = create_income(db_session, other_user, income_category)

    data = {
        "name": "bad actor",
        "date": "2025-01-01",
        "amount": 10.0,
        "category": income_category,
    }
    response = client.patch(f"/finances/edit_income/{income.id}",
                            data=json.dumps(data),
                            content_type="application/json")

    assert response.status_code == 404


def test_edit_income_not_found(client, auth):
    auth.login()
    data = json.dumps({
                        "name": "Test",
                        "date": "2025-01-01",
                        "amount": 10,
                        "category": 1,
                    })
    response = client.patch("/finances/edit_income/9999",
                            data=data,
                            content_type="application/json")
    assert response.status_code == 404


def test_edit_income_requires_patch(client):
    response = client.get("/finances/edit_income/1", follow_redirects=True)
    assert response.status_code == 405
    response = client.post("/finances/edit_income/1", follow_redirects=True)
    assert response.status_code == 405


def test_edit_income_requires_login(client):
    response = client.patch("/finances/edit_income/1", follow_redirects=True)
    assert b"login" in response.data


def test_delete_income_success(client, auth, app, db_session,
                               income_category):
    auth.login()
    user = User.query.filter_by(email="test@test.com").first()
    income = create_income(db_session, user, income_category)

    response = client.delete(f"/finances/delete_income/{income.id}")
    assert response.status_code == 200
    assert response.get_json()["success"]

    with app.app_context():
        assert db_session.get(Income, income.id) is None


def test_delete_income_requires_login(client):
    response = client.delete("/finances/delete_income/1",
                             follow_redirects=True)
    assert b"login" in response.data


def test_delete_income_other_user_forbidden(client, auth, db_session,
                                            income_category):
    auth.login()
    other_user = User.query.filter_by(email="second@test.com").first()
    income = create_income(db_session, other_user, income_category)

    response = client.delete(f"/finances/delete_income/{income.id}")
    assert response.status_code == 404


def test_delete_income_not_found(client, auth):
    auth.login()
    response = client.delete("/finances/delete_income/99999")
    assert response.status_code == 404


def test_delete_income_requires_delete(client):
    response = client.get("/finances/delete_income/1",
                          follow_redirects=True)
    assert response.status_code == 405
    response = client.post("/finances/delete_income/1",
                           follow_redirects=True)
    assert response.status_code == 405
