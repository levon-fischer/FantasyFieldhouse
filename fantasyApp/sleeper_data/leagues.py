from datetime import datetime

from celery import shared_task
from fantasyApp.sleeper_data.seasons import NewSeason
from fantasyApp.sleeper_data.utils import SleeperAPI
from fantasyApp.models import League, Season
from fantasyApp import db
from flask import current_app


class LeagueTree:
    def __init__(self, current_season):
        self.league_id = None
        self.current_season = current_season
        # Check if the league exists in our database already
        self.league_in_db = self.check_if_added(current_season)
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

    seasons_to_add = []

    def check_if_added(self, current_season):
        current_season_id = current_season.get("league_id")
        season_in_db = Season.query.filter_by(id=current_season_id).first()
        if season_in_db:
            current_app.logger.info(
                f"League for {current_season_id} already exists in our database"
            )
            return True

    def add_seasons(self):
        new_seasons = []
        while self.seasons_to_add:
            season_data = self.seasons_to_add.pop()
            new_seasons.append(NewSeason(season_data, self.league_id).db_item)
        db.session.add_all(new_seasons)

    def add_league_to_db(self):
        league = League(name=self.current_season.get("name"))
        db.session.add(league)
        self.league_id = league.id
        current_app.logger.info(
            f"Added league for {self.current_season.get('league_id')} to our database"
        )

    def dfs_for_seasons_to_add(self, season_data):
        prev_season_id = season_data.get("previous_league_id")
        # if there is a previous season
        if prev_season_id:
            # check if it exists in our database
            prev_season_in_db = Season.query.filter_by(id=prev_season_id).first()
            if not prev_season_in_db:
                # if it doesn't, add to list of seasons to add and continue down the graph
                self.seasons_to_add.append(season_data)
                self.dfs_for_seasons_to_add(
                    SleeperAPI.fetch_league_details(prev_season_id)
                )
            else:
                # if it does, we found our league so grab the league_id and start to add the new seasons to the db
                self.league_id = prev_season_in_db.league
                self.league_in_db = True


# @shared_task(name="check_for_new_leagues")
def check_for_new_leagues(user_id):
    current_year = datetime.now().year

    # Fetch the user's current leagues
    leagues_data = SleeperAPI.fetch_user_leagues(user_id, current_year)

    if leagues_data:  # If the user has leagues
        current_app.logger.info(f"Found {len(leagues_data)} leagues for user {user_id}")
        for league_data in leagues_data:  # For each league
            league = LeagueTree(league_data)
