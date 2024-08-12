from fantasyApp.sleeper_data.utils import SleeperAPI
from fantasyApp.models import Player
from fantasyApp import db
from flask import current_app


def add_players():
    players = SleeperAPI.fetch_all_players()
    players_to_add = []
    for player_id, player in players.items():
        players_to_add.append(
            Player(
                id=player_id,
                first_name=player.get("first_name"),
                last_name=player.get("last_name"),
                number=player.get("number"),
                position=player.get("fantasy_positions")[0],
                nfl_team=player.get("team"),
                age=player.get("age"),
                status=player.get("status"),
                years_exp=player.get("years_exp"),
                height=player.get("height"),
                weight=player.get("weight"),
                injury_status=player.get("injury_status"),
            )
        )
    db.session.add_all(players_to_add)
    db.session.commit()
