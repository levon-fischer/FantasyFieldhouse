from fantasyApp import db
from fantasyApp.models import Matchup, MatchupPlayer, MatchupTeam, Team
from fantasyApp.sleeper_data.utils import SleeperAPI, preprocess_bracket_data
from collections import defaultdict

from flask import current_app


class NewMatchup:
    def __init__(self, matchup, season_id, week):
        self.matchup = matchup
        self.season = season_id
        self.week = week
        self.matchup_id = int(
            str(self.season) + str(self.week) + str(self.matchup.get("matchup_id"))
        )
        self.team = int(str(self.season) + str(self.matchup.get("roster_id")))
        self.players = self.matchup.get("players")
        self.starters = self.matchup.get("starters")
        self.points = self.matchup.get("players_points")

        self.add_players()
        self.add_team()

        db.session.add_all(self.players_to_add)

    players_to_add = []

    def create_matchup_db_item(self, matchup_type="Regular", place=None):
        matchup = Matchup(
            id=self.matchup_id,
            week=self.week,
            matchup_type=matchup_type,
            place=place,
        )
        return matchup

    def add_player(self, player, starter, points):
        players = MatchupPlayer(
            matchup=self.matchup_id,
            player=player,
            starter=starter,
            points=points,
            team=self.team,
        )
        return players

    def add_players(self):
        for player in self.players:
            starter = player in self.starters
            points = self.points.get(player)

            self.players_to_add.append(self.add_player(player, starter, points))

    def add_team(self):
        team = MatchupTeam(
            Matchup=self.matchup_id,
            team=self.team,
            total_points=self.matchup.get("points"),
        )
        db.session.add(team)
