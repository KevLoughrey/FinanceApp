from financeapp.database import db
from financeapp.finances.models import ExpenseCategory


def init_db():
    default_categories = ['Mortgage', 'Rent', 'Groceries',
                          'Utilities', 'Transport', 'Other']
    for cat in default_categories:
        if not ExpenseCategory.query.filter_by(name=cat).first():
            db.session.add(ExpenseCategory(name=cat))
    db.session.commit()
