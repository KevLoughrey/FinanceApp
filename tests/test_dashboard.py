from financeapp.finances.models import Expense, ExpenseCategory
from financeapp.accounts.models import User
from financeapp.finances.utils import get_category_totals
from datetime import date
from decimal import Decimal
from sqlalchemy.engine import Row


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


def test_dashboard_requires_login(client):
    response = client.get("/finances/dashboard",  follow_redirects=True)
    assert b"login" in response.data


def test_dashboard_get(client, auth):
    auth.login()
    response = client.get("/finances/dashboard")
    assert response.status_code == 200
    assert b"dashboard" in response.data


def test_get_date_range_requires_login(client):
    response = client.get("finances/get_date_range")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_get_date_range_returns_json(client, auth, db_session,
                                     expense_category):
    auth.login()
    user = User.query.filter_by(email="test@test.com").first()

    create_expense(db_session, user, expense_category)

    response = client.get('finances/get_date_range',
                          query_string={"start": "2025-01", "end": "2025-12"})
    assert response.status_code == 200
    json_data = response.get_json()

    assert "expense_data" in json_data
    assert "income_data" in json_data
    assert "monthly_data" in json_data

    assert isinstance(json_data["expense_data"], list)
    assert any(d["category"] == "Mortgage" for d in json_data["expense_data"])


def test_get_category_totals_returns_list_of_rows(auth,
                                                  db_session,
                                                  expense_category):
    auth.login()
    user = User.query.filter_by(email="test@test.com").first()
    create_expense(db_session, user, expense_category)

    totals = get_category_totals(Expense, ExpenseCategory, user.id)
    assert isinstance(totals, list)
    assert all(isinstance(t, Row) for t in totals)
    assert all(isinstance(t[0], str) and
               (isinstance(t[1], (float, int, Decimal))
                or t[1] is None) for t in totals)
