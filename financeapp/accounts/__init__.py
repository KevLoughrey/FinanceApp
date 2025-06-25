from flask_security import SQLAlchemyUserDatastore
from .models import User, Role, ExtendedRegistrationForm # noqa F401
from database import db

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
