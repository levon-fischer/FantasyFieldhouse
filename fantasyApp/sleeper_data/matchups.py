from fantasyApp import db
from fantasyApp.models import Matchup, Team
from fantasyApp.sleeper_data.utils import SleeperAPI, preprocess_bracket_data
from collections import defaultdict

from flask import current_app


def add_matchup(
    matchup_data,
    opponent_data,
    season_id,
    league_id,
    week,
    roster_map,
    is_playoff=False,
    is_consolation=False,
    is_championship=False,
    is_toilet_bowl=False,
):
    matchup_id = str(season_id) + str(week) + str(matchup_data["matchup_id"])
    if matchup_data["points"] > opponent_data["points"]:
        win = True
        tie = False
    elif matchup_data["points"] == 0:
        win = False
        tie = False
    elif matchup_data["points"] == opponent_data["points"]:
        tie = True
        win = False
    else:
        win = False
        tie = False
    matchup = Matchup(
        matchup_id=matchup_id,
        sleeper_roster_id=matchup_data["roster_id"],
        week=week,
        points_for=matchup_data["points"],
        points_against=opponent_data["points"],
        win=win,
        tie=tie,
        playoff=is_playoff,
        consolation=is_consolation,
        championship=is_championship,
        toilet_bowl=is_toilet_bowl,
        league_id=league_id,
        season_id=season_id,
        team_id=roster_map[matchup_data["roster_id"]]["team_id"],
        owner_id=roster_map[matchup_data["roster_id"]]["owner_id"],
        opponent_team_id=roster_map[opponent_data["roster_id"]]["team_id"],
        opponent_owner_id=roster_map[opponent_data["roster_id"]]["owner_id"],
    )
    db.session.add(matchup)
    db.session.commit()


def add_matchups_from_season(
    season_id, league_id, roster_map, start_week, playoff_start
):
    for week in range(start_week, playoff_start):
        more_weeks = add_matchups_from_week(season_id, league_id, week, roster_map)
        if not more_weeks:
            break


def add_matchups_from_week(season_id, league_id, week, roster_map):
    matchups_data = SleeperAPI.fetch_matchups(season_id, week)
    if matchups_data:
        matchup_dict = defaultdict(list)
        for matchup_data in matchups_data:
            matchup_id = matchup_data["matchup_id"]
            if matchup_id is None:
                continue
            matchup_dict[matchup_id].append(matchup_data)
        for matchup_id, matchups in matchup_dict.items():
            current_app.logger.info(
                f"Adding matchup: week->{week}, roster_id->{matchups[0]['roster_id']}"
            )
            add_matchup(
                matchup_data=matchups[0],
                opponent_data=matchups[1],
                season_id=season_id,
                league_id=league_id,
                week=week,
                roster_map=roster_map,
            )
            current_app.logger.info(
                f"Adding matchup: week->{week}, roster_id->{matchups[1]['roster_id']}"
            )
            add_matchup(
                matchup_data=matchups[1],
                opponent_data=matchups[0],
                season_id=season_id,
                league_id=league_id,
                week=week,
                roster_map=roster_map,
            )
        return True
    else:
        return False


def add_postseason_matchups_from_season(
    season_id, league_id, roster_map, playoff_start, total_teams
):
    current_app.logger.info(f"Playoff start: {playoff_start}")
    bracket_data = preprocess_bracket_data(season_id, total_teams)
    round = 1
    current_app.logger.info(f"Season id: {season_id}")
    current_app.logger.info(f"Bracket data: {bracket_data}")
    more_weeks = add_postseason_matchups_from_week(
        season_id,
        league_id,
        round,
        playoff_start,
        roster_map,
        bracket_data,
        total_teams,
    )
    week = playoff_start + 1
    round += 1
    while more_weeks:
        more_weeks = add_postseason_matchups_from_week(
            season_id, league_id, round, week, roster_map, bracket_data, total_teams
        )
        week += 1
        round += 1


def process_single_matchup(
    matchup_data,
    opponent_data,
    season_id,
    league_id,
    week,
    round,
    roster_map,
    bracket_data,
    total_teams,
):
    roster_id = matchup_data["roster_id"]
    matchup_info = bracket_data.get((round, roster_id), {})
    current_app.logger.info(f"Matchup info: {matchup_info}")
    placement = matchup_info.get("placement", None)
    team_id = roster_map[roster_id]["team_id"]

    if placement is not None:
        team = Team.query.filter_by(id=team_id).first()
        team.place = placement
        db.session.commit()

    is_playoff = matchup_info.get("type") == "playoff"
    is_consolation = matchup_info.get("type") == "consolation"
    is_championship = placement is not None and placement <= 2
    is_toilet_bowl = placement is not None and placement >= total_teams - 1
    current_app.logger.info(
        f"Adding postseason matchup: week->{week}, roster_id->{roster_id}"
    )
    add_matchup(
        matchup_data=matchup_data,
        opponent_data=opponent_data,
        season_id=season_id,
        league_id=league_id,
        week=week,
        roster_map=roster_map,
        is_playoff=is_playoff,
        is_consolation=is_consolation,
        is_championship=is_championship,
        is_toilet_bowl=is_toilet_bowl,
    )


def add_postseason_matchups_from_week(
    season_id, league_id, round, week, roster_map, bracket_data, total_teams
):
    matchups_data = SleeperAPI.fetch_matchups(season_id, week)
    if matchups_data:
        matchup_dict = defaultdict(list)

        for matchup_data in matchups_data:
            matchup_id = matchup_data["matchup_id"]
            if matchup_id is None:
                continue
            matchup_dict[matchup_id].append(matchup_data)

        for matchup_id, matchups in matchup_dict.items():
            process_single_matchup(
                matchups[0],
                matchups[1],
                season_id,
                league_id,
                week,
                round,
                roster_map,
                bracket_data,
                total_teams,
            )
            process_single_matchup(
                matchups[1],
                matchups[0],
                season_id,
                league_id,
                week,
                round,
                roster_map,
                bracket_data,
                total_teams,
            )

        return True
    else:
        return False
