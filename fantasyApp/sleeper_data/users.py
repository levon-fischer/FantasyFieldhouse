from fantasyApp.sleeper_data.utils import SleeperAPI
from fantasyApp.models import User
from fantasyApp import db


def register_user(username, email, password):
    user = User.query.filter_by(username=username).first()
    if user: # If the user exists in our database already
        # update that user's email and password and registration status
        user.email = email
        user.password = password
        user.registered = True
        db.session.commit()

    else: # If the user does not exist in our database
        user_data = SleeperAPI.fetch_user(username)
        user = User(
            id=user_data['user_id'],
            username=user_data['username'],
            email=email,
            password=password,
            registered=True
        )
        db.session.add(user)
        db.session.commit()


def add_unregistered_user(user_id):
    pass
