from sqlalchemy import func

from fantasyApp.sleeper_data.utils import SleeperAPI
from fantasyApp.models import User
from fantasyApp import db
from flask import current_app


def register_user(username, email, password):
    username = username.lower()
    user = User.query.filter_by(username=username).first()
    if user:  # If the user exists in our database already
        # update that user's email and password and registration status
        user.email = email
        user.password = password
        user.registered = True
        db.session.commit()
        return user.id

    else:  # If the user does not exist in our database
        user_data = SleeperAPI.fetch_user(username)
        user = User(
            id=user_data["user_id"],
            username=user_data["username"].lower(),
            email=email,
            password=password,
            registered=True,
        )
        db.session.add(user)
        db.session.commit()
        return user_data["user_id"]


def add_unregistered_user(user_id, username):
    current_app.logger.info(f"Adding unregistered user {username} to our database")
    user = User(id=user_id, username=username.lower(), registered=False)
    db.session.add(user)
    db.session.commit()


def add_users_from_season(season_id):
    # Fetch the users from the season
    users_data = SleeperAPI.fetch_league_users(season_id)
    team_map = {}
    if users_data:  # If the season has users
        for user_data in users_data:
            # Grab user info to map to teams
            user_id = user_data["user_id"]
            team_map[user_id] = {}
            team_map[user_id]["team_name"] = user_data["metadata"].get(
                "team_name", "Unknown"
            )  # Default to 'Unknown' if not available
            commish_value = user_data.get("is_owner", False)
            if commish_value is None:
                commish_value = False
            team_map[user_id]["commish"] = commish_value
            # Check if the user exists in our database
            user = User.query.filter_by(id=user_id).first()
            if user:
                continue
            else:
                add_unregistered_user(user_id, user_data["display_name"])
    return team_map
