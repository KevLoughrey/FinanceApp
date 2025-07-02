from financeapp.database import db
from financeapp.finances.models import ExpenseCategory, IncomeCategory
from sqlalchemy import func


def init_db():
    default_expense_categories = ['Mortgage', 'Rent', 'Groceries',
                                  'Utilities', 'Transport', 'Other']
    for cat in default_expense_categories:
        if not ExpenseCategory.query.filter_by(name=cat).first():
            db.session.add(ExpenseCategory(name=cat))

    default_income_categories = ['Salary', 'Freelance', 'Savings',
                                 'Benefits', 'Gifts', 'Other']
    for cat in default_income_categories:
        if not IncomeCategory.query.filter_by(name=cat).first():
            db.session.add(IncomeCategory(name=cat))

    db.session.commit()


def get_category_totals(model, category_model, user_id):
    return (
        db.session.query(category_model.name, func.sum(model.amount))
        .join(category_model)
        .filter(model.user_id == user_id)
        .group_by(category_model.name)
        .all()
    )


def get_monthly_totals(model, user_id, start_date=None, end_date=None):
    query = db.session.query(
        func.date_trunc('month', model.date).label('month'),
        func.sum(model.amount)
    ).filter(model.user_id == user_id)

    if start_date:
        query = query.filter(model.date >= start_date)
    if end_date:
        query = query.filter(model.date <= end_date)

    return query.group_by('month').order_by('month').all()


def get_monthly_chart_data(expense_monthly, income_monthly):
    all_months = sorted(
        set(row[0] for row in expense_monthly + income_monthly)
    )
    month_labels = [m.strftime('%B %Y') for m in all_months]

    expense_dict = {
        m.strftime('%B %Y'): float(v) for m, v in expense_monthly
    }
    income_dict = {
        m.strftime('%B %Y'): float(v) for m, v in income_monthly
    }

    return {
        'months': month_labels,
        'expenses': [expense_dict.get(m, 0) for m in month_labels],
        'income': [income_dict.get(m, 0) for m in month_labels],
    }