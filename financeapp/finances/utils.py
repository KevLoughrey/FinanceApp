from financeapp.database import db
from financeapp.finances.models import ExpenseCategory, IncomeCategory


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
