from flask_security.models import fsqla_v3 as fsqla
from flask_security.forms import RegisterForm
from wtforms import StringField
from wtforms.validators import DataRequired
from database import db

fsqla.FsModels.set_db_info(db)


class Role(db.Model, fsqla.FsRoleMixin):
    pass


class User(db.Model, fsqla.FsUserMixin):
    username = db.Column(db.String(50), unique=True, nullable=False)


class ExtendedRegistrationForm(RegisterForm):
    username = StringField('Username', validators=[DataRequired()])