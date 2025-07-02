from financeapp.database import db
from financeapp.finances.models import ExpenseCategory, IncomeCategory
from sqlalchemy import func, extract
from datetime import datetime


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


def get_category_totals(model, category_model, user_id,
                        start_date=None, end_date=None):
    query = (
        db.session.query(category_model.name, func.sum(model.amount))
        .join(category_model)
        .filter(model.user_id == user_id)
    )

    if start_date:
        query = query.filter(model.date >= start_date)
    if end_date:
        query = query.filter(model.date <= end_date)

    return query.group_by(category_model.name).all()


def get_monthly_totals(model, user_id, start_date=None, end_date=None):
    query = db.session.query(
        extract('year', model.date).label('year'),
        extract('month', model.date).label('month'),
        func.sum(model.amount).label('total')
    ).filter(model.user_id == user_id)

    if start_date:
        query = query.filter(model.date >= start_date)
    if end_date:
        query = query.filter(model.date <= end_date)

    query = query.group_by('year', 'month').order_by('year', 'month')

    return query.all()


def get_monthly_chart_data(expense_monthly, income_monthly):
    all_months = sorted(
        set((row[0], row[1]) for row in expense_monthly + income_monthly)
    )

    month_labels = [
        datetime(int(year), int(month), 1).strftime('%B %Y') 
        for year, month in all_months
    ]

    expense_dict = {(row[0], row[1]): float(row[2]) for row in expense_monthly}
    income_dict = {(row[0], row[1]): float(row[2]) for row in income_monthly}

    expense_totals = [
        expense_dict.get((year, month), 0) for year, month in all_months]
    income_totals = [
        income_dict.get((year, month), 0) for year, month in all_months]

    return {
        'months': month_labels,
        'expenses': expense_totals,
        'income': income_totals,
    }
