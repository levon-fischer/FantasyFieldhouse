from fantasyApp import db
from fantasyApp.models import Team
from fantasyApp.sleeper_data.utils import SleeperAPI
from flask import current_app


def add_team(team_data, team_id, season_id, league_id, year, name, commish):
    current_app.logger.info(f"Adding team {team_id}|{name} to our database")
    team = Team(
        id=team_id,  # Season ID + Roster ID
        season_id=season_id,
        league_id=league_id,
        user_id=team_data["owner_id"],
        sleeper_roster_id=team_data["roster_id"],
        name=name,
        year=year,
        wins=team_data["settings"]["wins"],
        losses=team_data["settings"]["losses"],
        ties=team_data["settings"]["ties"],
        points_for=team_data["settings"]["fpts"],
        is_commish=commish,
    )
    db.session.add(team)
    db.session.commit()


def add_teams_from_season(season_id, league_id, year, team_map):
    # Fetch the teams from the season
    teams_data = SleeperAPI.fetch_league_rosters(season_id)
    if teams_data:  # If the season has teams
        roster_map = {}
        for team_data in teams_data:
            owner_id = team_data.get("owner_id", None)
            if owner_id is None:
                continue
            name = team_map.get(owner_id, {}).get("team_name", "Unknown")
            commish = team_map.get(owner_id, {}).get("commish", False)
            team_id = str(season_id) + str(team_data["roster_id"])
            roster_id = team_data["roster_id"]
            roster_map[roster_id] = {}
            roster_map[roster_id]["owner_id"] = owner_id
            roster_map[roster_id]["team_id"] = team_id
            add_team(team_data, team_id, season_id, league_id, year, name, commish)
        return roster_map
