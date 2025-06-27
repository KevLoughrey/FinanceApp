from flask_security import SQLAlchemyUserDatastore
from financeapp.accounts.models import User, Role
from financeapp.database import db
from financeapp.accounts.routes import profiles_bp  # noqa

user_datastore = SQLAlchemyUserDatastore(db, User, Role)