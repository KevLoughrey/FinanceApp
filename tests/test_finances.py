from financeapp.finances.models import ExpenseCategory, Expense
from financeapp.accounts.models import User
from datetime import date
from decimal import Decimal


def test_create_expense_category(db_session):
    category = ExpenseCategory(name="Rent")
    db_session.add(category)
    db_session.commit()

    assert category.id is not None
    assert str(category) == "Rent"


def test_create_expense(db_session):
    user = User.query.filter_by(email="test@example.com").first()
    category = ExpenseCategory(name="Mortgage")
    db_session.add(category)
    db_session.commit()

    expense = Expense(
        name="Mortgage Payment",
        date=date(2025, 6, 1),
        description="June mortgage payment",
        amount=Decimal("1050.25"),
        user_id=user.id,
        category_id=category.id
    )
    db_session.add(expense)
    db_session.commit()

    assert expense.id is not None
    assert expense.name == "Mortgage Payment"
    assert expense.amount == Decimal("1050.25")
    assert expense.user == user
    assert expense.category.name == "Mortgage"


def test_add_expense_get(client, auth):
    auth.login()
    response = client.get("/finances/add_expense")
    assert response.status_code == 200
    assert b"Add Expense" in response.data


def test_add_expense_post(client, auth, app, category):
    auth.login()
    response = client.post("/finances/add_expense", data={
        "name": "Test Expense",
        "date": "2025-01-01",
        "description": "Test description",
        "amount": "123.45",
        "category": category,
    }, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        expense = Expense.query.filter_by(name="Test Expense").first()
        assert expense is not None
        assert float(expense.amount) == 123.45


def test_my_finances(client, auth):
    auth.login()
    response = client.get("/finances/my_finances")
    assert response.status_code == 200
    assert b"my_finances" in response.data
