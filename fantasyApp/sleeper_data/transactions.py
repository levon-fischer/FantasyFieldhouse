from fantasyApp import db
from fantasyApp.models import Transaction, Claim, TradedItem
from fantasyApp.sleeper_data.utils import SleeperAPI


class NewTransaction:
    def __init__(self, transaction, week, season_id):
        self.transaction = transaction
        self.transaction_id = transaction.get("transaction_id")
        self.creator = transaction.get("creator")
        self.time_created = transaction.get("created")  # Need to convert this
        self.time_processed = transaction.get("status_updated")  # Need to convert this
        self.week = week
        self.season = season_id
        self.transaction_type = transaction.get("type")
        self.transaction_items = []

        if self.transaction_type == "trade":
            self.type = "trade"
            self.transaction_items.append(self.add_trade_items())
        else:
            self.type = "claim"
            self.transaction_items.append(self.add_claim_items())

    def create_db_item(self):
        transaction = Transaction(
            id=self.transaction_id,
            creator=self.creator,
            time_created=self.time_created,
            time_processed=self.time_processed,
            week=self.week,
            season=self.season,
            type=self.type,
        )
        self.transaction_items.append(transaction)

        return self.transaction_items

    def add_claim_items(self):
        # If "adds" exists in the transaction, get the first player id from it.
        # If "adds" doesn't exist, set added_player to None.
        added_player = (
                self.transaction.get("adds")
                and list(self.transaction.get("adds").keys())[0]
        )
        # If "drops" exists in the transaction, get the first player id from it.
        # If "drops" doesn't exist, set dropped_player to None.
        dropped_player = (
                self.transaction.get("drops")
                and list(self.transaction.get("drops").keys())[0]
        )
        settings = self.transaction.get("settings")

        claim = Claim(
            transaction=self.transaction_id,
            type=self.transaction_type,
            status=self.transaction.get("status"),
            added_player=added_player,
            dropped_player=dropped_player,
            waiver_order=settings.get("seq"),
            bid=settings.get("bid"),
        )
        return claim

    def add_trade_items(self):
        pass
