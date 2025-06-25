from flask import Blueprint, render_template
from flask_security import login_required

home_bp = Blueprint('home', __name__, template_folder='templates')


@home_bp.route('/')
@login_required
def index():
    return render_template('home/index.html')
