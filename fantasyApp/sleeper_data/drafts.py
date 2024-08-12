from fantasyApp import db
from fantasyApp.models import Draft, DraftPosition, DraftPick
from fantasyApp.sleeper_data.utils import SleeperAPI
from flask import current_app
from datetime import datetime


class NewDraft:
    def __init__(self, draft):
        self.draft = draft
        self.draft_id = draft.get("draft_id")
        self.settings = draft.get("settings")
        self.league_id = draft.get("league_id")
        self.draft_slots = SleeperAPI.fetch_draft_data(self.draft_id).get(
            "slot_to_roster_id"
        )
        self.draft_picks = SleeperAPI.fetch_draft_picks(self.draft_id)

        self.create_draft_positions()
        self.create_draft_picks()
        db.session.add_all(self.draft_items_to_add)

    draft_items_to_add = []

    def create_draft_db_item(self):
        draft = Draft(
            id=self.draft_id,
            status=self.draft.get("status"),
            year=self.draft.get("season"),
            start_time=datetime.fromtimestamp(self.draft.get("start_time") / 1000),
            type=self.draft.get("type"),
            rounds=self.settings.get("rounds"),
            pick_timer=self.settings.get("pick_timer"),
            scoring_type=self.draft.get("metadata").get("scoring_type"),
            season=self.league_id,
        )
        return draft

    def create_draft_positions(self):
        for position, roster_id in self.draft_slots.items():
            team_id = int(str(self.league_id) + str(roster_id))
            self.draft_items_to_add.append(
                DraftPosition(draft=self.draft_id, team=team_id, position=position)
            )

    def create_draft_picks(self):
        if self.draft_picks:
            for pick in self.draft_picks:
                team_id = int(str(self.league_id) + str(pick.get("roster_id")))
                self.draft_items_to_add.append(
                    DraftPick(
                        round=pick.get("round"),
                        pick_num=pick.get("pick_no"),
                        slot=pick.get("draft_slot"),
                        keeper=pick.get("is_keeper"),
                        draft=self.draft_id,
                        team=team_id,
                        player=pick.get("player_id"),
                    )
                )
