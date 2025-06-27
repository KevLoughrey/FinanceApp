from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, DecimalField,
                     SelectField, DateField, SubmitField)
from wtforms.validators import DataRequired, Length, NumberRange
from financeapp.finances.models import ExpenseCategory


class ExpenseForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    amount = DecimalField(
        'Amount',
        places=2,
        rounding=None,
        validators=[
            DataRequired(),
            NumberRange(min=0, message="Amount must be a positive number.")
        ]
    )
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Expense')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category.choices = [
            (c.id, c.name) for c in ExpenseCategory.query.order_by('name')
        ]
