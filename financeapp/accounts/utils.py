import os
from database import db
from .models import User
from flask_security.utils import hash_password
from . import user_datastore


def init_db():
    db.create_all()

    if not User.query.filter_by(email=os.getenv("ADMIN_EMAIL")).first():
        user_datastore.create_user(
            email=os.getenv("ADMIN_EMAIL"),
            username=os.getenv("ADMIN_USERNAME"),
            password=hash_password(os.getenv("ADMIN_PASSWORD"))
        )
        db.session.commit()
