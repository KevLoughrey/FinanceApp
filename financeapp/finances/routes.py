from flask import (Blueprint, render_template, redirect,
                   url_for, request, jsonify)
from flask_security import login_required, current_user
from financeapp.finances.forms import ExpenseForm, IncomeForm
from financeapp.finances.models import (Expense, ExpenseCategory,
                                        Income, IncomeCategory)
from financeapp.database import db


finances_bp = Blueprint('finances', __name__, template_folder='templates')


@finances_bp.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    form = ExpenseForm()
    if request.method == "POST":
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
    expense_categories = ExpenseCategory.query.order_by(
        ExpenseCategory.name).all()

    incomes = (
        Income.query
        .filter_by(user_id=current_user.id)
        .order_by(Income.date.desc())
        .all()
    )
    income_categories = IncomeCategory.query.order_by(
        IncomeCategory.name).all()

    context = {
        'expenses': expenses,
        'expense_categories': expense_categories,
        'incomes': incomes,
        'income_categories': income_categories,
    }

    return render_template("finances/my_finances.html", **context)


@finances_bp.route("/edit_expense/<int:id>", methods=["POST"])
@login_required
def edit_expense(id):
    expense = Expense.query.filter_by(id=id,
                                      user_id=current_user.id).first_or_404()
    data = request.get_json()

    for key, value in data.items():
        if value is None:
            data[key] = ''
    form = ExpenseForm(data=data, meta={'csrf': False})

    form.category.choices = [
        (c.id, c.name) for c in ExpenseCategory.query.order_by('name').all()]

    if form.validate():
        expense.name = form.name.data
        expense.date = form.date.data
        expense.description = form.description.data
        expense.amount = form.amount.data
        expense.category_id = form.category.data

        db.session.commit()

        return jsonify({
            "success": True,
            "expense": {
                "id": expense.id,
                "name": expense.name,
                "date": expense.date.strftime('%Y-%m-%d'),
                "description": expense.description or '',
                "amount": str(expense.amount),
                "category_id": expense.category_id,
                "category_name": expense.category.name
            }
        })

    else:
        return jsonify({"success": False, "errors": form.errors})


@finances_bp.route("/delete_expense/<int:id>", methods=["DELETE"])
@login_required
def delete_expense(id):
    expense = Expense.query.filter_by(id=id,
                                      user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    return jsonify({"success": True})


@finances_bp.route('/add_income', methods=['GET', 'POST'])
@login_required
def add_income():
    form = IncomeForm()
    if request.method == "POST":
        if form.validate_on_submit():
            income = Income(
                name=form.name.data,
                date=form.date.data,
                description=form.description.data,
                amount=form.amount.data,
                category_id=form.category.data,
                user_id=current_user.id
            )
            db.session.add(income)
            db.session.commit()
            return redirect(url_for('finances.my_finances'))

    context = {
        'form': form,
    }

    return render_template('finances/add_income.html', **context)
