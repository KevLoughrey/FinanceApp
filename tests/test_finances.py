from financeapp.finances.models import ExpenseCategory, Expense
from financeapp.accounts.models import User
from financeapp.finances.utils import init_db
from datetime import date
from decimal import Decimal


def test_db_create_expense_category(db_session):
    category = ExpenseCategory(name="Rent")
    db_session.add(category)
    db_session.commit()

    assert category.id is not None
    assert str(category) == "Rent"


def test_db_create_expense(db_session):
    user = User.query.filter_by(email="test@test.com").first()
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


def test_finance_init_db_creates_default_categories(app, db_session):
    with app.app_context():
        init_db()
        categories = [cat.name for cat in ExpenseCategory.query.all()]
        assert set(categories) == {'Mortgage', 'Rent', 'Groceries',
                                   'Utilities', 'Transport', 'Other'}


def test_finance_init_db_does_not_duplicate(app, db_session):
    with app.app_context():
        db_session.add(ExpenseCategory(name='Groceries'))
        db_session.commit()

        init_db()

        count = ExpenseCategory.query.filter_by(name='Groceries').count()
        assert count == 1


def test_add_expense_requires_login(client, auth):
    response = client.get("/finances/add_expense")
    assert response.status_code == 302
    assert b"login" in response.data


def test_add_expense_get(client, auth):
    auth.login()
    response = client.get("/finances/add_expense")
    assert response.status_code == 200
    assert b"Add Expense" in response.data


def test_add_expense_success(client, auth, app, category):
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


def test_add_expense_missing_required_fields(client, auth):
    auth.login()
    response = client.post("/finances/add_expense", data={},
                           follow_redirects=True)
    assert response.status_code == 200
    assert response.data.count(b"This field is required") >= 3


def test_add_expense_negative_amount(client, auth, category):
    auth.login()
    response = client.post("/finances/add_expense", data={
        "name": "Test Expense",
        "date": "2025-01-01",
        "description": "Test description",
        "amount": "-50.00",
        "category": category,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Amount must be a positive number" in response.data


def test_add_expense_invalid_date_format(client, auth, category):
    auth.login()
    response = client.post("/finances/add_expense", data={
        "name": "Test Expense",
        "date": "lorem",
        "description": "Test description",
        "amount": "123.45",
        "category": category,
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


def test_add_expense_amount_not_a_number(client, auth, category):
    auth.login()
    response = client.post("/finances/add_expense", data={
        "name": "Test Expense",
        "date": "2025-01-01",
        "description": "Test description",
        "amount": "lorem",
        "category": category,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"This field is required" in response.data


def test_my_finances_requires_login(client, auth):
    response = client.get("/finances/my_finances")
    assert response.status_code == 302
    assert b"login" in response.data


def test_my_finances_get(client, auth):
    auth.login()
    response = client.get("/finances/my_finances")
    assert response.status_code == 200
    assert b"my_finances" in response.data
