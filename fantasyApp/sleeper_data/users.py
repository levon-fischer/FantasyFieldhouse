from sqlalchemy import func

from fantasyApp.sleeper_data.utils import SleeperAPI
from fantasyApp.models import User
from fantasyApp import db
from flask import current_app


def add_unregistered_user(user_id: int, username: str) -> None:
    """
    Add an unregistered user to the database.
    :param user_id:
    :param username:
    :return:
    """
    current_app.logger.info(f"Adding unregistered user {username} to our database")
    user = User(id=user_id, username=username.lower(), registered=False)
    db.session.add(user)
    db.session.commit()


def add_users_from_season(season_id: int) -> dict:
    """
    Add users from a season to the database.
    :param season_id: The ID of the season.
    :return: A dictionary mapping user IDs to team names and whether they are the commissioner.
    """
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


class NewUser:
    """
    A class to represent a new user.
    :ivar user: The user data from the Sleeper API.
    :ivar user_id: The ID of the user.
    :ivar username: The username of the user.
    :ivar email: The email of the user.
    :ivar password: The password of the user.
    """
    def __init__(self, user):
        self.user = user
        self.user_id = user.get("user_id")

    def __init__(self, username: str, email: str, password: str) -> None:
        self.username = username.lower()
        self.email = email.lower()
        self.password = password
        self.register_user()

    def register_user(self) -> None:
        """
        Register the user in the database by setting the email, password, and registered attributes.
        :return:
        """
        # If the user is already in the database, register them and update their email and password
        user = User.query.filter_by(username=self.username).first()
        if user:
            user.email = self.email
            user.password = self.password
            user.registered = True
            self.user_id = user.id
        else:  # Otherwise create a new user
            db.session.add(self.create_registered_db_item(self.email, self.password))
        db.session.commit()

    def create_unregistered_db_item(self) -> User:
        """
        Create an unregistered user item for the database.
        :return: A User object with only an id and username.
        """
        user = User(
            id=self.user.get("user_id"),
            username=self.user.get("username").lower,
            registered=False,
        )
        return user

    def create_registered_db_item(self, email: str, password: str) -> User:
        """
        Create a registered user item for the database.
        :param email: The email of the user.
        :param password: The password of the user.
        :return: A User object with an id, username, email, password, and registered status.
        """
        user = User(
            id=self.user.get("user_id"),
            username=self.user.get("username").lower,
            email=email,
            password=password,
            registered=True,
        )
        self.user_id = user.id
        return user
