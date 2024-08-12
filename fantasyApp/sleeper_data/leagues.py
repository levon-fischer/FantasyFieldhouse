from datetime import datetime

from celery import shared_task
from fantasyApp.sleeper_data.seasons import NewSeason
from fantasyApp.sleeper_data.utils import SleeperAPI
from fantasyApp.models import League, Season
from fantasyApp import db
from flask import current_app


def check_if_added(current_season: dict) -> bool:
    """
    Check if the league is already in the database.
    :param current_season: The league data returned from the sleeper API.
    :return: True if the league is in the database, False otherwise.
    """
    current_season_id = current_season.get("league_id")
    season_in_db = Season.query.filter_by(id=current_season_id).first()
    if season_in_db:
        current_app.logger.info(
            f"League for {current_season_id} already exists in our database"
        )
        return True
    return False


class LeagueTree:
    """
    A class to represent the league tree and manage league and season data.

    :ivar league_id: The ID of the league.
    :ivar current_season: The current season data.
    :ivar league_in_db: Whether the league is in the database.
    :ivar seasons_to_add: A list of seasons to add.
    """
    seasons_to_add = []

    def __init__(self, current_season: dict) -> None:
        """
        Initialize the LeagueTree with the current season's data.
        :param current_season: The league data returned from the sleeper API.
        """
        self.league_id = None
        self.current_season = current_season
        # Check if the league exists in our database already
        self.league_in_db = check_if_added(current_season)
        # If it doesn't, search through each previous season until we find the league
        if not self.league_in_db:
            self.seasons_to_add.append(current_season)
            self.dfs_for_seasons_to_add(current_season)
            # If we didn't find a league, create a new one
            if not self.league_in_db:
                self.add_league_to_db()
                self.league_in_db = True
            # Add any new seasons found and then commit everything to the database
            self.add_seasons()
            db.session.commit()

    def add_seasons(self) -> None:
        """
        Add the new seasons in seasons_to_add to the database.
        :return:
        """
        new_seasons = []
        while self.seasons_to_add:
            season_data = self.seasons_to_add.pop()
            # Create a new season object and add it to the database
            new_seasons.append(NewSeason(season_data, self.league_id).db_item)
        db.session.add_all(new_seasons)

    def add_league_to_db(self) -> None:
        """
        Add the league to the database.
        :return:
        """
        # Create a new League object
        league = League(name=self.current_season.get("name"))
        db.session.add(league)
        # After adding to the database, save the newly generated league_id
        self.league_id = league.id
        current_app.logger.info(
            f"Added league for {self.current_season.get('league_id')} to our database"
        )

    def dfs_for_seasons_to_add(self, season_data: dict) -> None:
        """
        Perform a depth-first search through previous seasons to find the league in the database.
        It grabs the previous season and then checks if it exists in the database. If it doesn't, it adds it to a list of
        seasons to add the database later and then continues on to the next season. If it does exist, it grabs the
        league_id and starts to add the new seasons to the database.
        :param season_data: The league data from the sleeper API
        :return:
        """
        prev_season_id = season_data.get("previous_league_id")
        # if there is a previous season
        if prev_season_id:
            # check if it exists in our database
            prev_season_in_db = Season.query.filter_by(id=prev_season_id).first()
            if not prev_season_in_db:
                # if it doesn't, add it to the list of seasons to add
                self.seasons_to_add.append(season_data)
                # and then continue down the graph by calling this function recursively with the previous season
                self.dfs_for_seasons_to_add(
                    SleeperAPI.fetch_league_details(prev_season_id)
                )
            else:
                # if it does, we found our league so grab the league_id and start to add the new seasons to the db
                self.league_id = prev_season_in_db.league
                self.league_in_db = True


# @shared_task(name="check_for_new_leagues")
def check_for_new_leagues(user_id: int) -> None:
    """
    Check for new leagues for a user and add them to the database.
    :param user_id: The ID of the user to check for new leagues.
    :return: None
    """
    current_year = datetime.now().year

    # Fetch the user's current leagues
    leagues_data = SleeperAPI.fetch_user_leagues(user_id, current_year)

    if leagues_data:  # If the user has leagues
        current_app.logger.info(f"Found {len(leagues_data)} leagues for user {user_id}")
        for league_data in leagues_data:  # For each league
            league = LeagueTree(league_data)
