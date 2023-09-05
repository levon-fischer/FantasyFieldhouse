from datetime import datetime

from fantasyApp.sleeper_data.matchups import (
    add_matchups_from_season,
    add_postseason_matchups_from_season,
)
from fantasyApp.sleeper_data.teams import add_teams_from_season
from fantasyApp.sleeper_data.users import add_users_from_season
from fantasyApp.sleeper_data.utils import SleeperAPI
from fantasyApp.models import Season
from fantasyApp import db
from flask import current_app


def add_season_from_data(season_data, league_id):
    # Create a season for the league
    season_id = season_data["league_id"]
    current_app.logger.info(f"Adding season {season_id} to our database")
    year = season_data["season"]
    total_teams = season_data["total_rosters"]
    playoff_start = season_data["settings"]["playoff_week_start"]
    season = Season(
        id=season_id,
        league_id=league_id,
        name=season_data["name"],
        total_teams=total_teams,
        year=year,
        season_type=season_data["season_type"],
        playoff_week_start=playoff_start,
        draft_id=season_data["draft_id"],
    )
    db.session.add(season)
    db.session.commit()
    # Add the users from the season to the database
    team_map = add_users_from_season(season_data["league_id"])
    # Add the teams from the season to the database
    roster_map = add_teams_from_season(season_id, league_id, year, team_map)
    # Add the matchups from the season to the database
    # Get the start week for the season, if it doesn't exit, default to 1
    start_week = season_data["settings"].get("start_week", 1)
    add_matchups_from_season(
        season_id, league_id, roster_map, start_week, playoff_start
    )

    current_year = datetime.now().year
    if year != current_year:
        current_app.logger.info(
            f"Starting postseason matchups. year {year} | sys year {current_year}"
        )
        add_postseason_matchups_from_season(
            season_id, league_id, roster_map, playoff_start, total_teams
        )


def add_season_from_api(season_id, league_id):
    # Fetch the season data from the API
    season_data = SleeperAPI.fetch_league_details(season_id)
    # Add the season to our database
    add_season_from_data(season_data, league_id)
    # Return the previous season id
    return season_data["previous_league_id"]


def update_league_ids(season_id, league_id):
    while season_id:
        season_data = SleeperAPI.fetch_league_details(season_id)
        season = Season.query.filter_by(id=season_id).first()
        season.league_id = league_id
        db.session.commit()
        season_id = season_data["previous_league_id"]
