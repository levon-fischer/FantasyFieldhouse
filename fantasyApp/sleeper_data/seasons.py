from datetime import datetime

from fantasyApp.sleeper_data.teams import NewTeam
from fantasyApp.sleeper_data.drafts import NewDraft
from fantasyApp.sleeper_data.users import NewUser
from fantasyApp.sleeper_data.matchups import NewMatchup
from fantasyApp.sleeper_data.utils import SleeperAPI, preprocess_bracket_data
from fantasyApp.models import Season, User, Division
from fantasyApp import db
from flask import current_app


class NewSeason:
    def __init__(self, season, league_id):
        self.season = season
        self.season_id = season.get("league_id")
        self.league_id = league_id
        self.users = []
        self.teams = []
        self.matchups = []

        self.year = season.get("season")
        self.total_teams = season.get("total_rosters")

        self.settings = season.get("settings")
        self.start_week = self.settings.get("start_week")
        self.playoff_start = self.settings.get("playoff_week_start")
        self.scoring = self.settings.get("scoring_settings")
        self.positions = self.settings.get("roster_positions")

        self.db_item = self.create_db_item()

    new_users = []
    new_teams = []
    new_matchups = []
    new_drafts = []
    new_transactions = []

    team_name_map = {}
    division_map = {}

    def create_db_item(self):
        season = Season(
            id=self.season_id,
            name=self.season.get("name"),
            year=self.year,
            num_teams=self.total_teams,
            status=self.season.get("status"),
            season_type=self.season.get("season_type"),
            pts_rush_yds=self.scoring.get("rush_yd"),
            pts_rush_td=self.scoring.get("rush_td"),
            pts_rec_yds=self.scoring.get("rec_yd"),
            pts_rec_td=self.scoring.get("rec_td"),
            pts_pass_yds=self.scoring.get("pass_yd"),
            pts_pass_td=self.scoring.get("pass_td"),
            pts_bonus_rec_te=self.scoring.get("bonus_rec_te"),
            qb=self.positions.count("QB"),
            rb=self.positions.count("RB"),
            wr=self.positions.count("WR"),
            te=self.positions.count("TE"),
            w_r_t=self.positions.count("FLEX"),
            w_r=self.positions.count("WRRB_FLEX"),
            w_t=self.positions.count("REC_FLEX"),
            q_w_r_t=self.positions.count("SUPER_FLEX"),
            k=self.positions.count("K"),
            dst=self.positions.count("DST"),
            bn=self.positions.count("BN"),
            ir=self.settings.get("reserve_slots"),
            taxi=self.settings.get("taxi_slots"),
            dl=self.positions.count("DL"),
            lb=self.positions.count("LB"),
            db=self.positions.count("DB"),
            idp_flex=self.positions.count("IDP_FLEX"),
            pick_trading=bool(self.settings.get("pick_trading")),
            playoffs_start_wk=self.playoff_start,
            num_poff_teams=self.settings.get("playoff_teams"),
            last_league_champ=self.season.get("metadata").get(
                "latest_league_winner_roster_id", None
            ),
            league=self.league_id,
            previous_season=self.season_data.get("previous_league_id"),
        )
        return season

    def get_new_users(self):
        users_data = SleeperAPI.fetch_league_users(self.season_id)
        if users_data:
            for user_data in users_data:
                user_id = user_data.get("user_id")
                self.team_name_map[user_id] = {
                    "team_name": user_data.get("metadata").get("team_name"),
                    "commish": user_data.get("is_owner"),
                }

                in_db = User.query.filter_by(id=user_id).first()
                if not in_db:
                    self.new_users.append(
                        NewUser(user_data).create_unregistered_db_item()
                    )

    def get_new_divisions(self):
        metadata = self.season.get("metadata")
        for key, value in metadata.items():
            if key.startswith("division_") and not key.endswith("_avatar"):
                division_number = key.split("_")[1]
                division_name = value
                division = Division(
                    name=division_name,
                    number=division_number,
                    season=self.season_id,
                )
                db.session.add(division)
                db.session.flush()
                self.divison_map[division_number] = division.id

    def get_new_teams(self):
        teams_data = SleeperAPI.fetch_league_rosters(self.season_id)
        if teams_data:
            for team_data in teams_data:
                division = self.division_map.get(
                    team_data.get("settings").get("division")
                )
                self.new_teams.append(
                    NewTeam(
                        team_data,
                        self.season_id,
                        self.league_id,
                        self.team_name_map[team_data.get("owner_id")],
                        self.year,
                        division,
                    ).create_team_db_item()
                )

    def get_new_drafts(self):
        drafts_data = SleeperAPI.fetch_league_drafts(self.season_id)
        if drafts_data:
            for draft_data in drafts_data:
                self.new_drafts.append(NewDraft(draft_data))

    def get_new_matchups(self):
        # Regular Season Matchups
        for week in range(self.start_week, self.playoff_start):
            matchups_data = SleeperAPI.fetch_matchups(self.season_id, week)
            matchups = []
            for matchup in matchups_data:
                id = matchup.get("matchup_id")
                if id not in matchups:
                    matchups.append(id)
                    self.new_matchups.append(
                        NewMatchup(
                            matchup, self.season_id, week
                        ).create_matchup_db_item()
                    )
                else:
                    NewMatchup(matchup, self.season_id, week)
        # Post Season Matchups
        bracket = preprocess_bracket_data(self.season_id)
        round = 1
        week = self.playoff_start
        postseason_week = SleeperAPI.fetch_matchups(self.season_id, week)
        while postseason_week:
            bracket_data = bracket.get(round)
            matchups = []
            for matchup in postseason_week:
                id = matchup.get("matchup_id")

                if id not in matchups:
                    matchups.append(id)
                    team_id = matchup.get("roster_id")
                    match_data = bracket_data.get(team_id)
                    postseason_type = match_data.get("type")
                    place = match_data.get("place")
                    self.new_matchups.append(
                        NewMatchup(
                            matchup, self.season_id, week
                        ).create_matchup_db_item(postseason_type, place)
                    )
                else:
                    NewMatchup(matchup, self.season_id, week)
            round += 1
            week += 1
            postseason_week = SleeperAPI.fetch_matchups(self.season_id, week)

    def get_new_transactions(self):
        pass
