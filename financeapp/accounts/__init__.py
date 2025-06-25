from flask import Blueprint, render_template
from flask_security import SQLAlchemyUserDatastore
from .models import User, Role
from database import db
from flask_login import current_user
from flask_security import login_required

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
profiles_bp = Blueprint('profile', __name__, template_folder='templates')


@profiles_bp.route('/')
@login_required
def profile():
    context = {
        'user': current_user,
    }
    return render_template('accounts/profile.html', **context)
