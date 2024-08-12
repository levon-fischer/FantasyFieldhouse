from datetime import datetime
from itsdangerous.timed import TimedSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
from flask import current_app
from fantasyApp import db, login_manager
from flask_login import UserMixin

Model = db.Model
Column = db.Column
Integer = db.Integer
Float = db.Float
String = db.String
Boolean = db.Boolean
DateTime = db.DateTime
Text = db.Text
ForeignKey = db.ForeignKey
relationship = db.relationship


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(Model, UserMixin):
    # Primary Key
    id = Column(Integer, primary_key=True)
    # Attributes
    username = Column(String(64), index=True, unique=False, nullable=False)
    registered = Column(
        Boolean, index=False, unique=False, nullable=False, default=False
    )
    email = Column(String(120), index=True, unique=True, nullable=True)
    # TODO: switch to importing their sleeper avatar
    image_file = Column(
        String(20), index=False, unique=False, nullable=True, default="default.jpg"
    )
    password = Column(String(60), index=False, unique=False, nullable=True)
    # Relationships
    posts = relationship("Post", backref="author", lazy="dynamic")

    def get_reset_token(self):
        s = Serializer(current_app.config["SECRET_KEY"])  # Create a serializer object
        return s.dumps({"user_id": self.id}).decode(
            "utf-8"
        )  # Return a token with the user id

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token, max_age=1800)["user_id"]  # Try to load the token
        except (SignatureExpired, BadSignature):
            return None
        return User.query.get(user_id)  # Return the user with the user id

    def __repr__(self):
        return f"<User {self.username}, {self.email}, {self.image_file}>"


class Post(Model):
    # Primary Key
    id = Column(Integer, primary_key=True)
    # Attributes
    title = Column(String(100), index=False, unique=False, nullable=False)
    date_posted = Column(
        DateTime, index=False, unique=False, nullable=False, default=datetime.utcnow
    )
    content = Column(Text, index=False, unique=False, nullable=False)
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"<Post {self.title}, {self.date_posted}>"


class League(Model):
    # Primary Key
    id = Column(Integer, primary_key=True)
    # Attributes
    name = Column(String(64), index=False, unique=False, nullable=False)

    def __repr__(self):
        return f"<League {self.name}>"


class Season(Model):
    # Primary Key
    id = Column(Integer, primary_key=True)
    # Attributes
    name = Column(String(64), index=False, unique=False, nullable=True)
    year = Column(Integer, index=False, unique=False, nullable=False)
    num_teams = Column(Integer, index=False, unique=False, nullable=False)
    status = Column(String(64), index=False, unique=False, nullable=True)
    season_type = Column(String(64), index=False, unique=False, nullable=True)
    pts_rush_yds = Column(Integer, index=False, unique=False, nullable=False)
    pts_rush_td = Column(Integer, index=False, unique=False, nullable=False)
    pts_rec_yds = Column(Integer, index=False, unique=False, nullable=False)
    pts_rec_td = Column(Integer, index=False, unique=False, nullable=False)
    pts_pass_yds = Column(Integer, index=False, unique=False, nullable=False)
    pts_pass_td = Column(Integer, index=False, unique=False, nullable=False)
    pts_bonus_rec_te = Column(Integer, index=False, unique=False, nullable=False)
    qb = Column(Integer, index=False, unique=False, nullable=False)
    rb = Column(Integer, index=False, unique=False, nullable=False)
    wr = Column(Integer, index=False, unique=False, nullable=False)
    te = Column(Integer, index=False, unique=False, nullable=False)
    w_r_t = Column(Integer, index=False, unique=False, nullable=False)
    w_r = Column(Integer, index=False, unique=False, nullable=False)
    w_t = Column(Integer, index=False, unique=False, nullable=False)
    q_w_r_t = Column(Integer, index=False, unique=False, nullable=False)
    k = Column(Integer, index=False, unique=False, nullable=False)
    dst = Column(Integer, index=False, unique=False, nullable=False)
    bn = Column(Integer, index=False, unique=False, nullable=False)
    ir = Column(Integer, index=False, unique=False, nullable=False)
    taxi = Column(Integer, index=False, unique=False, nullable=False)
    dl = Column(Integer, index=False, unique=False, nullable=False)
    lb = Column(Integer, index=False, unique=False, nullable=False)
    db = Column(Integer, index=False, unique=False, nullable=False)
    idp_flex = Column(Integer, index=False, unique=False, nullable=False)
    pick_trading = Column(Boolean, index=False, unique=False, nullable=False)
    playoffs_start_wk = Column(Integer, index=False, unique=False, nullable=True)
    num_poff_teams = Column(Integer, index=False, unique=False, nullable=True)
    last_league_champ = Column(Integer, index=False, unique=False, nullable=True)
    # Foreign Keys
    league = Column(
        Integer, ForeignKey("league.id"), index=False, unique=False, nullable=False
    )
    previous_season = Column(
        Integer, ForeignKey("season.id"), index=False, unique=False, nullable=True
    )


class Division(Model):
    # Primary Key
    id = Column(Integer, primary_key=True)
    # Attributes
    name = Column(String(64), index=False, unique=False, nullable=True)
    number = Column(Integer, index=False, unique=False, nullable=True)
    # Foreign Keys
    season = Column(
        Integer, ForeignKey("season.id"), index=False, unique=False, nullable=False
    )


class Team(Model):
    # Primary Key
    id = Column(
        Integer, primary_key=True
    )  # Create with league_id + roster_id from sleeper API
    # Attributes
    sleeper_roster_id = Column(Integer, index=False, unique=False, nullable=False)
    name = Column(String(64), index=False, unique=False, nullable=False)
    year = Column(Integer, index=False, unique=False, nullable=False)
    is_commish = Column(Boolean, index=False, unique=False, nullable=False)
    place = Column(Integer, index=False, unique=False, nullable=True)
    # Foreign Keys
    division = Column(
        Integer, ForeignKey("division.id"), index=False, unique=False, nullable=True
    )
    owner = Column(
        Integer, ForeignKey("user.id"), index=False, unique=False, nullable=True
    )
    season = Column(
        Integer, ForeignKey("season.id"), index=False, unique=False, nullable=False
    )
    league = Column(
        Integer, ForeignKey("league.id"), index=False, unique=False, nullable=False
    )


class Player(Model):
    # Primary Key
    id = Column(Integer, primary_key=True)
    # Attributes
    first_name = Column(String(64), index=False, unique=False, nullable=False)
    last_name = Column(String(64), index=False, unique=False, nullable=False)
    number = Column(Integer, index=False, unique=False, nullable=True)
    position = Column(String(5), index=False, unique=False, nullable=False)
    nfl_team = Column(String(3), index=False, unique=False, nullable=True)
    age = Column(Integer, index=False, unique=False, nullable=False)
    status = Column(String(64), index=False, unique=False, nullable=False)
    years_exp = Column(Integer, index=False, unique=False, nullable=False)
    weight = Column(Integer, index=False, unique=False, nullable=False)
    height = Column(Integer, index=False, unique=False, nullable=False)
    injury_status = Column(String(24), index=False, unique=False, nullable=False)


class TeamPlayer(Model):
    # Primary keys
    team = Column(
        Integer, ForeignKey("team.id"), primary_key=True, unique=False, nullable=False
    )
    player = Column(
        Integer, ForeignKey("player.id"), primary_key=True, unique=False, nullable=False
    )
    nickname = Column(String(64), index=False, unique=False, nullable=True)


class Matchup(Model):
    # Primary Key
    id = Column(Integer, primary_key=True)
    # Attributes
    week = Column(Integer, index=False, unique=False, nullable=False)
    matchup_type = Column(
        db.Enum("regular", "playoff", "consolation"),
        index=False,
        unique=False,
        nullable=False,
    )
    place = Column(Integer, index=False, unique=False, nullable=True)


class MatchupTeam(Model):
    # Primary Keys
    matchup = Column(
        Integer,
        ForeignKey("matchup.id"),
        primary_key=True,
        index=True,
        unique=False,
        nullable=False,
    )
    team = Column(
        Integer,
        ForeignKey("team.id"),
        primary_key=True,
        index=True,
        unique=False,
        nullable=False,
    )
    # Attributes
    total_points = Column(Float, index=False, unique=False, nullable=True)


class MatchupPlayer(Model):
    # Primary Keys
    matchup = Column(
        Integer,
        ForeignKey("matchup.id"),
        primary_key=True,
        index=True,
        unique=False,
        nullable=False,
    )
    player = Column(
        Integer,
        ForeignKey("player.id"),
        primary_key=True,
        index=True,
        unique=False,
        nullable=False,
    )
    # Attributes
    starter = Column(Boolean, index=False, unique=False, nullable=False)
    points = Column(Float, index=False, unique=False, nullable=True)
    # Foreign Key
    team = Column(
        Integer, ForeignKey("team.id"), index=False, unique=False, nullable=False
    )


class Transaction(Model):
    # Primary Key
    id = Column(Integer, primary_key=True)
    # Attributes
    type = Column(db.Enum("trade", "claim"), index=False, unique=False, nullable=False)
    week = Column(Integer, index=False, unique=False, nullable=False)
    time_created = Column(DateTime, index=False, unique=False, nullable=False)
    time_processed = Column(DateTime, index=False, unique=False, nullable=True)
    # Foreign Keys
    season = Column(
        Integer, ForeignKey("season.id"), index=False, unique=False, nullable=False
    )
    creator = Column(
        Integer, ForeignKey("user.id"), index=False, unique=False, nullable=False
    )


class Claim(Model):
    # Primary Key
    id = Column(Integer, primary_key=True)
    # Attributes
    type = Column(
        db.Enum("Waiver", "Free Agent"), index=False, unique=False, nullable=False
    )
    status = Column(
        db.Enum("Complete", "Failed"), index=False, unique=False, nullable=False
    )
    waiver_order = Column(Integer, index=False, unique=False, nullable=True)
    bid = Column(Integer, index=False, unique=False, nullable=True)
    # Foreign Keys
    transaction = Column(
        Integer, ForeignKey("transaction.id"), index=False, unique=False, nullable=False
    )
    added_player = Column(
        Integer, ForeignKey("player.id"), index=False, unique=False, nullable=True
    )
    dropped_player = Column(
        Integer, ForeignKey("player.id"), index=False, unique=False, nullable=True
    )


class TradedItem(Model):
    # Primary Key
    id = Column(Integer, primary_key=True)
    # Attributes
    item_type = Column(
        db.Enum("Player", "Pick", "FAAB"), index=False, unique=False, nullable=False
    )
    year = Column(
        Integer, index=False, unique=False, nullable=True
    )  # Used for picks only
    round = Column(
        Integer, index=False, unique=False, nullable=True
    )  # Used for picks only
    amount = Column(
        Integer, index=False, unique=False, nullable=True
    )  # Used for FAAB only
    ktc_score = Column(Integer, index=False, unique=False, nullable=True)
    # Foreign Keys
    transaction = Column(
        Integer, ForeignKey("transaction.id"), index=False, unique=False, nullable=False
    )
    player = Column(
        Integer, ForeignKey("player.id"), index=False, unique=False, nullable=True
    )
    old_team = Column(
        Integer, ForeignKey("team.id"), index=False, unique=False, nullable=False
    )
    new_team = Column(
        Integer, ForeignKey("team.id"), index=False, unique=False, nullable=False
    )
    orig_team = Column(
        Integer, ForeignKey("team.id"), index=False, unique=False, nullable=True
    )  # Used for picks only


class Draft(Model):
    # Primary Key
    id = Column(Integer, primary_key=True)
    # Attributes
    status = Column(String(64), index=False, unique=False, nullable=False)
    year = Column(Integer, index=False, unique=False, nullable=False)
    start_time = Column(DateTime, index=False, unique=False, nullable=True)
    type = Column(String(64), index=False, unique=False, nullable=False)
    rounds = Column(Integer, index=False, unique=False, nullable=False)
    pick_timer = Column(Integer, index=False, unique=False, nullable=False)
    scoring_type = Column(String(64), index=False, unique=False, nullable=False)
    # Foreign Keys
    season = Column(
        Integer, ForeignKey("season.id"), index=False, unique=False, nullable=False
    )


class DraftPosition(Model):
    # Primary Keys
    draft = Column(
        Integer,
        ForeignKey("draft.id"),
        primary_key=True,
        index=True,
        unique=False,
        nullable=False,
    )
    team = Column(
        Integer,
        ForeignKey("team.id"),
        primary_key=True,
        index=True,
        unique=False,
        nullable=False,
    )
    # Attributes
    position = Column(Integer, index=False, unique=False, nullable=False)


class DraftPick(Model):
    # Primary Key
    id = Column(Integer, primary_key=True)
    # Attributes
    round = Column(Integer, index=False, unique=False, nullable=False)
    pick_num = Column(Integer, index=False, unique=False, nullable=False)
    slot = Column(Integer, index=False, unique=False, nullable=False)
    keeper = Column(Boolean, index=False, unique=False, nullable=False)
    # Foreign Keys
    draft = Column(
        Integer, ForeignKey("draft.id"), index=False, unique=False, nullable=False
    )
    team = Column(
        Integer, ForeignKey("team.id"), index=False, unique=False, nullable=False
    )
    player = Column(
        Integer, ForeignKey("player.id"), index=False, unique=False, nullable=True
    )


class KtcValue(Model):
    # Primary Key
    id = Column(Integer, primary_key=True)
    # Attributes
    date_of_retrieval = Column(DateTime, index=True, unique=False, nullable=False)
    Value = Column(Integer, index=False, unique=False, nullable=False)
    # Foreign Keys
    player = Column(
        Integer, ForeignKey("player.id"), index=True, unique=False, nullable=False
    )


class NflState(db.Model):
    week = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.Integer, index=False, unique=False)
    season_type = db.Column(db.String(64), index=False, unique=False)
