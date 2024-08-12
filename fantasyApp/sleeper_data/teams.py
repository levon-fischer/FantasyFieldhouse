from fantasyApp import db
from fantasyApp.models import Team, TeamPlayer
from fantasyApp.sleeper_data.utils import SleeperAPI
from flask import current_app


class NewTeam:
    def __init__(self, team, season_id, league_id, map, year, division):
        self.team = team
        self.season_id = season_id
        self.league_id = league_id
        self.team_name = map.get("team_name")
        self.team_id = int(str(self.season_id) + str(self.roster_id))
        self.roster_id = team.get("roster_id")
        self.year = year
        self.owner = team.get("owner_id")
        self.is_commish = map.get("commish")
        self.division = division

        self.add_players()

    players_to_add = []

    def create_team_db_item(self):
        team = Team(
            id=self.team_id,
            sleeper_roster_id=self.roster_id,
            name=self.team_name,
            year=self.year,
            is_commish=self.is_commish,
            division=self.division,
            owner=self.owner,
            season=self.season_id,
            league=self.league_id,
        )
        return team

    def add_players(self):
        # TODO: Figure out how to match nicknames for the players
        players = self.team.get("players")
        players_to_add = []
        for player in players:
            players_to_add.append(TeamPlayer(team=self.team_id, player=player))
        db.session.add_all(players_to_add)
