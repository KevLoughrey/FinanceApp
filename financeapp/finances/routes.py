from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    jsonify,
)
from flask_security import (
    login_required,
    current_user,
)
from financeapp.finances.forms import (
    ExpenseForm,
    IncomeForm,
)
from financeapp.finances.models import (
    Expense,
    ExpenseCategory,
    Income,
    IncomeCategory,
)
from financeapp.finances.utils import (
    get_category_totals,
    get_monthly_totals,
    get_monthly_chart_data,
)
from financeapp.database import db
from datetime import datetime


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
            return redirect(url_for('finances.dashboard'))

    context = {
        'form': form,
    }

    return render_template('finances/add_expense.html', **context)


@finances_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = current_user.id

    context = {
        'expenses':
            Expense.query.filter_by(user_id=user_id)
            .order_by(Expense.date.desc()).all(),
        'expense_categories':
            ExpenseCategory.query
            .order_by(ExpenseCategory.name).all(),
        'incomes':
            Income.query.filter_by(user_id=user_id)
            .order_by(Income.date.desc()).all(),
        'income_categories':
            IncomeCategory.query
            .order_by(IncomeCategory.name).all(),
        'expense_data': get_category_totals(Expense, ExpenseCategory, user_id),
        'income_data': get_category_totals(Income, IncomeCategory, user_id),
    }

    expense_monthly = get_monthly_totals(Expense, user_id)
    income_monthly = get_monthly_totals(Income, user_id)
    context['monthly_data'] = get_monthly_chart_data(expense_monthly,
                                                     income_monthly)

    return render_template("finances/dashboard.html", **context)


@finances_bp.route("/edit_expense/<int:id>", methods=["PATCH"])
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
            return redirect(url_for('finances.dashboard'))

    context = {
        'form': form,
    }

    return render_template('finances/add_income.html', **context)


@finances_bp.route("/edit_income/<int:id>", methods=["PATCH"])
@login_required
def edit_income(id):
    income = Income.query.filter_by(id=id,
                                    user_id=current_user.id).first_or_404()
    data = request.get_json()

    for key, value in data.items():
        if value is None:
            data[key] = ''
    form = IncomeForm(data=data, meta={'csrf': False})

    form.category.choices = [
        (c.id, c.name) for c in IncomeCategory.query.order_by('name').all()]

    if form.validate():
        income.name = form.name.data
        income.date = form.date.data
        income.description = form.description.data
        income.amount = form.amount.data
        income.category_id = form.category.data

        db.session.commit()

        return jsonify({
            "success": True,
            "income": {
                "id": income.id,
                "name": income.name,
                "date": income.date.strftime('%Y-%m-%d'),
                "description": income.description or '',
                "amount": str(income.amount),
                "category_id": income.category_id,
                "category_name": income.category.name
            }
        })

    else:
        return jsonify({"success": False, "errors": form.errors})


@finances_bp.route("/delete_income/<int:id>", methods=["DELETE"])
@login_required
def delete_income(id):
    income = Income.query.filter_by(id=id,
                                    user_id=current_user.id).first_or_404()
    db.session.delete(income)
    db.session.commit()
    return jsonify({"success": True})


@finances_bp.route("/get_date_range")
@login_required
def get_date_range():
    user_id = current_user.id
    start = request.args.get("start")
    end = request.args.get("end")

    start_date = datetime.strptime(start, "%Y-%m") if start else None
    end_date = datetime.strptime(end, "%Y-%m") if end else None

    raw_expense_totals = get_category_totals(
        Expense, ExpenseCategory, user_id, start_date, end_date)
    expense_totals = [
        {"category": row[0], "total": float(row[1])}
        for row in raw_expense_totals
    ]

    raw_income_totals = get_category_totals(
        Income, IncomeCategory, user_id, start_date, end_date)
    income_totals = [
        {"category": row[0], "total": float(row[1])}
        for row in raw_income_totals
    ]

    expense_monthly = get_monthly_totals(
        Expense, user_id, start_date, end_date)
    income_monthly = get_monthly_totals(Income, user_id, start_date, end_date)
    monthly_data = get_monthly_chart_data(expense_monthly, income_monthly)

    return jsonify({
        'expense_data': expense_totals,
        'income_data': income_totals,
        'monthly_data': monthly_data
    })
