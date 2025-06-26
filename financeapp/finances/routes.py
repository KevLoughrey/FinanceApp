from flask import Blueprint, render_template, redirect, url_for
from flask_security import login_required, current_user
from .forms import ExpenseForm
from .models import Expense, db

finances_bp = Blueprint('finances', __name__, template_folder='templates')


@finances_bp.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(
            name=form.name.data,
            date=form.date.data,
            description=form.description.data,
            amount=form.amount.data,
            category_id=form.category.data,
            user_id=current_user.id
        )
        db.session.add(expense)
        db.session.commit()
        return redirect(url_for('finances.my_finances'))

    context = {
        'form': form,
    }

    return render_template('finances/add_expense.html', **context)


@finances_bp.route("/my_finances")
@login_required
def my_finances():
    expenses = (
        Expense.query
        .filter_by(user_id=current_user.id)
        .order_by(Expense.date.desc())
        .all()
    )

    context = {
        'expenses': expenses,
    }

    return render_template("finances/my_finances.html", **context)
