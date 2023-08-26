from fantasyApp import db
from fantasyApp.models import Team
from fantasyApp.sleeper_data.utils import SleeperAPI


def add_team(team_data, season_id, year, name, commish):
    team_id = int(str(season_id) + str(team_data['roster_id']))
    team = Team(
        id=team_id, # Season ID + Roster ID
        season_id=season_id,
        user_id=team_data['owner_id'],
        name=name,
        year=year,
        wins=team_data['settings']['wins'],
        losses=team_data['settings']['losses'],
        ties=team_data['settings']['ties'],
        points_for=team_data['settings']['fpts'],
        points_for_decimal=team_data['settings']['fpts_decimal'],
        points_against=team_data['settings']['fpts_against'],
        points_against_decimal=team_data['settings']['fpts_against_decimal'],
        total_moves=team_data['settings']['total_moves'],
        is_commish=commish
    )
    db.session.add(team)
    db.session.commit()
def add_teams_from_season(season_id, year, team_map):
    # Fetch the teams from the season
    teams_data = SleeperAPI.fetch_league_rosters(season_id)
    if teams_data: # If the season has teams
        for team_data in teams_data:
            name = team_map[team_data['owner_id']]['team_name']
            commish = team_map[team_data['owner_id']]['commish']
            add_team(team_data, season_id, year, name, commish)