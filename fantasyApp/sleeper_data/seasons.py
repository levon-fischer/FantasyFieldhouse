from fantasyApp.sleeper_data.teams import add_teams_from_season
from fantasyApp.sleeper_data.users import add_users_from_season
from fantasyApp.sleeper_data.utils import SleeperAPI
from fantasyApp.models import Season
from fantasyApp import db

def add_season_from_data(season_data, league_id):
    # Create a season for the league
    season = Season(
        id=season_data['id'],
        league_id=league_id,
        name=season_data['name'],
        total_teams=season_data['total_rosters'],
        year=season_data['season'],
        season_type=season_data['season_type'],
        draft_id=season_data['draft_id'],
    )
    db.session.add(season)
    db.session.commit()
    # Add the users from the season to the database
    team_map = add_users_from_season(season_data['id'])
    # Add the teams from the season to the database
    add_teams_from_season(season_data['id'], season_data['season'], team_map)


def add_season_from_api(season_id, league_id):
    # Fetch the season data from the API
    season_data = SleeperAPI.fetch_league_details(season_id)
    # Add the season to our database
    add_season_from_data(season_data, league_id)
    # Return the previous season id
    return season_data['previous_league_id']


def update_league_ids(season_id, league_id):
    while season_id:
        season_data = SleeperAPI.fetch_league_details(season_id)
        season = Season.query.filter_by(id=season_id).first()
        season.league_id = league_id
        db.session.commit()
        season_id = season_data['previous_league_id']
