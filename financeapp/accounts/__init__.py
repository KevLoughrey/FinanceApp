from flask_security import SQLAlchemyUserDatastore
from .models import User, Role
from database import db
from .routes import profiles_bp # noqa

user_datastore = SQLAlchemyUserDatastore(db, User, Role)