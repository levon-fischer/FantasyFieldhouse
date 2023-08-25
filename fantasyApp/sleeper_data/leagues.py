from fantasyApp.sleeper_data.utils import SleeperAPI
from fantasyApp.models import League
from fantasyApp import db


def add_or_update_league(league_id):
    league_data = SleeperAPI.fetch_league_details(league_id)
    if league_data:
        league = League(id=league_id, name=league_data['name'], total_teams=league_data['total_rosters'], num_seasons=league_data['seasons'])
        db.session.add(league)
        db.session.commit()