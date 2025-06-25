from flask import Blueprint
from flask_security import SQLAlchemyUserDatastore
from .models import User, Role, ExtendedRegistrationForm
from database import db

user_datastore = SQLAlchemyUserDatastore(db, User, Role)