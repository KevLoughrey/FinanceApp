from financeapp.finances.models import ExpenseCategory, Expense
from financeapp.accounts.models import User
from financeapp.finances.utils import init_db
from datetime import date
from decimal import Decimal
import json


def create_expense(db_session, user, expense_category):
    expense = Expense(
        name="Mortgage Payment",
        date=date(2025, 6, 1),
        description="June mortgage payment",
        amount=Decimal("1050.25"),
        user_id=user.id,
        category_id=expense_category
    )
    db_session.add(expense)
    db_session.commit()
    return expense


def test_db_create_expense_category(db_session):
    category = ExpenseCategory(name="Rent")
    db_session.add(category)
    db_session.commit()

    assert category.id is not None
    assert str(category) == "Rent"


def test_db_create_expense(db_session, expense_category):
    user = User.query.filter_by(email="test@test.com").first()
    expense = create_expense(db_session, user, expense_category)

    assert expense.id is not None
    assert expense.name == "Mortgage Payment"
    assert expense.amount == Decimal("1050.25")
    assert expense.user == user
    assert expense.category.name == "Mortgage"


def test_finance_init_db_creates_default_categories(app, db_session):
    with app.app_context():
        init_db()
        categories = [cat.name for cat in ExpenseCategory.query.all()]
        assert set(categories) == {'Mortgage', 'Rent', 'Groceries',
                                   'Utilities', 'Transport', 'Other'}


def test_finance_init_db_does_not_duplicate(app, db_session):
    with app.app_context():
        db_session.add(ExpenseCategory(name='Mortgage'))
        db_session.commit()

        init_db()

        count = ExpenseCategory.query.filter_by(name='Mortgage').count()
        assert count == 1


def test_add_expense_requires_login(client, auth):
    response = client.get("/finances/add_expense", follow_redirects=True)
    assert b"login" in response.data


def test_add_expense_get(client, auth):
    auth.login()
    response = client.get("/finances/add_expense")
    assert response.status_code == 200
    assert b"Add Expense" in response.data


def test_add_expense_success(client, auth, app, expense_category):
    auth.login()
    response = client.post("/finances/add_expense", data={
        "name": "Test Expense",
        "date": "2025-01-01",
        "description": "Test description",
        "amount": "123.45",
        "category": expense_category,
    }, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        expense = Expense.query.filter_by(name="Test Expense").first()
        assert expense is not None
        assert float(expense.amount) == 123.45


def test_add_expense_missing_required_fields(client, auth):
    auth.login()
    response = client.post("/finances/add_expense", data={},
                           follow_redirects=True)
    assert response.status_code == 200
    assert response.data.count(b"This field is required") >= 3


def test_add_expense_negative_amount(client, auth, expense_category):
    auth.login()
    response = client.post("/finances/add_expense", data={
        "name": "Test Expense",
        "date": "2025-01-01",
        "description": "Test description",
        "amount": "-50.00",
        "category": expense_category,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Amount must be a positive number" in response.data


def test_add_expense_invalid_date_format(client, auth, expense_category):
    auth.login()
    response = client.post("/finances/add_expense", data={
        "name": "Test Expense",
        "date": "lorem",
        "description": "Test description",
        "amount": "123.45",
        "category": expense_category,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"This field is required" in response.data


def test_add_expense_invalid_category(client, auth):
    auth.login()
    response = client.post("/finances/add_expense", data={
        "name": "Test Expense",
        "date": "2025-01-01",
        "description": "Test description",
        "amount": "123.45",
        "category": 1000,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Not a valid choice" in response.data


def test_add_expense_amount_not_a_number(client, auth, expense_category):
    auth.login()
    response = client.post("/finances/add_expense", data={
        "name": "Test Expense",
        "date": "2025-01-01",
        "description": "Test description",
        "amount": "lorem",
        "category": expense_category,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"This field is required" in response.data


def test_edit_expense_success(client, auth, db_session, expense_category):
    auth.login()
    user = User.query.filter_by(email="test@test.com").first()
    expense = create_expense(db_session, user, expense_category)

    data = {
        "name": "Updated Name",
        "date": "1999-07-01",
        "description": "Updated description",
        "amount": 999.99,
        "category": expense_category,
    }
    response = client.patch(f"/finances/edit_expense/{expense.id}",
                            data=json.dumps(data),
                            content_type="application/json")

    assert response.status_code == 200
    result = response.get_json()
    assert result["success"]
    assert result["expense"]["name"] == "Updated Name"
    assert result["expense"]["description"] == "Updated description"
    assert result["expense"]["date"] == "1999-07-01"
    assert result["expense"]["amount"] == "999.99"
    assert result["expense"]["category_id"] == 1


def test_edit_expense_invalid_category(client, auth, db_session,
                                       expense_category):
    auth.login()
    user = User.query.filter_by(email="test@test.com").first()
    expense = create_expense(db_session, user, expense_category)

    data = {
        "name": "Bad Category",
        "date": "2025-07-01",
        "description": "Invalid category",
        "amount": 50.00,
        "category": 1000,
    }
    response = client.patch(f"/finances/edit_expense/{expense.id}",
                            data=json.dumps(data),
                            content_type="application/json")

    assert not response.get_json()["success"]
    assert "category" in response.get_json()["errors"]


def test_edit_expense_negative_amount(client, auth, db_session,
                                      expense_category):
    auth.login()
    user = User.query.filter_by(email="test@test.com").first()
    expense = create_expense(db_session, user, expense_category)

    data = {
        "name": "Bad Amount",
        "date": "2025-07-01",
        "description": "Negative",
        "amount": -50.00,
        "category": expense_category,
    }
    response = client.patch(f"/finances/edit_expense/{expense.id}",
                            data=json.dumps(data),
                            content_type="application/json")

    assert not response.get_json()["success"]
    assert "amount" in response.get_json()["errors"]


def test_edit_expense_invalid_date(client, auth, db_session, expense_category):
    auth.login()
    user = User.query.filter_by(email="test@test.com").first()
    expense = create_expense(db_session, user, expense_category)

    data = {
        "name": "Bad Date",
        "date": "not-a-date",
        "description": "error",
        "amount": 10.00,
        "category": expense_category,
    }
    response = client.patch(f"/finances/edit_expense/{expense.id}",
                            data=json.dumps(data),
                            content_type="application/json")

    assert not response.get_json()["success"]
    assert "date" in response.get_json()["errors"]


def test_edit_expense_missing_fields(client, auth, db_session,
                                     expense_category):
    auth.login()
    user = User.query.filter_by(email="test@test.com").first()
    expense = create_expense(db_session, user, expense_category)

    response = client.patch(f"/finances/edit_expense/{expense.id}",
                            data=json.dumps({}),
                            content_type="application/json")

    assert not response.get_json()["success"]
    assert "name" in response.get_json()["errors"]
    assert "date" in response.get_json()["errors"]


def test_edit_expense_other_user_forbidden(client, auth,
                                           db_session, expense_category):
    auth.login()
    other_user = User.query.filter_by(email="second@test.com").first()
    expense = create_expense(db_session, other_user, expense_category)

    data = {
        "name": "bad actor",
        "date": "2025-01-01",
        "amount": 10.0,
        "category": expense_category,
    }
    response = client.patch(f"/finances/edit_expense/{expense.id}",
                            data=json.dumps(data),
                            content_type="application/json")

    assert response.status_code == 404


def test_edit_expense_not_found(client, auth):
    auth.login()
    data = json.dumps({
                        "name": "Test",
                        "date": "2025-01-01",
                        "amount": 10,
                        "category": 1,
                    })
    response = client.patch("/finances/edit_expense/9999",
                            data=data,
                            content_type="application/json")
    assert response.status_code == 404


def test_edit_expense_requires_patch(client):
    response = client.get("/finances/edit_expense/1", follow_redirects=True)
    assert response.status_code == 405
    response = client.post("/finances/edit_expense/1", follow_redirects=True)
    assert response.status_code == 405


def test_edit_expense_requires_login(client):
    response = client.patch("/finances/edit_expense/1", follow_redirects=True)
    assert b"login" in response.data


def test_delete_expense_success(client, auth, app, db_session,
                                expense_category):
    auth.login()
    user = User.query.filter_by(email="test@test.com").first()
    expense = create_expense(db_session, user, expense_category)

    response = client.delete(f"/finances/delete_expense/{expense.id}")
    assert response.status_code == 200
    assert response.get_json()["success"]

    with app.app_context():
        assert db_session.get(Expense, expense.id) is None


def test_delete_expense_requires_login(client):
    response = client.delete("/finances/delete_expense/1",
                             follow_redirects=True)
    assert b"login" in response.data


def test_delete_expense_other_user_forbidden(client, auth, db_session,
                                             expense_category):
    auth.login()
    other_user = User.query.filter_by(email="second@test.com").first()
    expense = create_expense(db_session, other_user, expense_category)

    response = client.delete(f"/finances/delete_expense/{expense.id}")
    assert response.status_code == 404


def test_delete_expense_not_found(client, auth):
    auth.login()
    response = client.delete("/finances/delete_expense/99999")
    assert response.status_code == 404


def test_delete_expense_requires_delete(client):
    response = client.get("/finances/delete_expense/1",
                          follow_redirects=True)
    assert response.status_code == 405
    response = client.post("/finances/delete_expense/1",
                           follow_redirects=True)
    assert response.status_code == 405
