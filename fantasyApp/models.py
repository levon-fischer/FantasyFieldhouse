from datetime import datetime
from itsdangerous.timed import TimedSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
from flask import current_app
from fantasyApp import db, login_manager
from flask_login import UserMixin


user_season_association = db.Table('user_season_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('season_id', db.Integer, db.ForeignKey('season.id'), primary_key=True)
)

user_league_association = db.Table('user_league_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('league_id', db.Integer, db.ForeignKey('league.id'), primary_key=True)
)

player_team_association = db.Table('player_team_association',
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True),
    db.Column('player_id', db.Integer, db.ForeignKey('player.id'), primary_key=True)
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # Attributes
    username = db.Column(db.String(64), index=True, unique=False, nullable=False)
    registered = db.Column(db.Boolean, index=True, unique=False, default=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    # TODO: switch to importing their sleeper avatar
    image_file = db.Column(
        db.String(20), index=False, unique=False, nullable=False, default="default.jpg"
    )
    password = db.Column(db.String(60), nullable=False)
    # Relationships
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    teams = db.relationship('Team', backref='owner', lazy='dynamic')
    matchups_as_owner = db.relationship('Matchup', foreign_keys='matchup.team_id', backref='user', lazy='dynamic')
    matchups_as_opponent = db.relationship('Matchup', foreign_keys='matchup.opponent_owner_id', backref='opponent_user', lazy='dynamic')
    # Many-to-many relationships
    seasons = db.relationship('Season', secondary=user_season_association, lazy='subquery',
                              backref=db.backref('users', lazy=True))
    leagues = db.relationship('League', secondary=user_league_association, lazy='subquery',
                              backref=db.backref('users', lazy=True))
    # display_name = db.Column(db.String(64), index=True, unique=True)
    # total_wins = db.Column(db.Integer, index=True, unique=False)
    # total_losses = db.Column(db.Integer, index=True, unique=False)
    # total_ties = db.Column(db.Integer, index=True, unique=False)
    # total_points_for = db.Column(db.Integer, index=True, unique=False)
    # total_points_against = db.Column(db.Integer, index=True, unique=False)
    # total_moves = db.Column(db.Integer, index=True, unique=False)
    # total_trades = db.Column(db.Integer, index=True, unique=False)


    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY']) # Create a serializer object
        return s.dumps({'user_id': self.id}).decode('utf-8') # Return a token with the user id

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=1800)['user_id'] # Try to load the token
        except (SignatureExpired, BadSignature):
            return None
        return User.query.get(user_id) # Return the user with the user id

    def __repr__(self):
        return f"<User {self.username}, {self.email}, {self.image_file}>"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Attributes
    title = db.Column(db.String(100), index=True, unique=False, nullable=False)
    date_posted = db.Column(
        db.DateTime, index=False, unique=False, nullable=False, default=datetime.utcnow
    )
    content = db.Column(db.Text, index=False, unique=False, nullable=False)
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"<Post {self.title}, {self.date_posted}>"


class League(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Attributes
    name = db.Column(db.String(64), index=False, unique=False)
    total_teams = db.Column(db.Integer, index=False, unique=False)
    num_seasons = db.Column(db.Integer, index=False, unique=False)
    # Foreign Keys
    current_season_id = db.Column(db.Integer, db.ForeignKey('season.id'), index=True, unique=True)
    # Relationships
    users = db.relationship('User', backref='league', lazy='dynamic') # many to many
    seasons = db.relationship('Season', backref='league', lazy='select')
    matchups = db.relationship('Matchup', backref='league', lazy='dynamic')
    teams = db.relationship('Team', backref='league', lazy='dynamic')
    current_season = db.relationship('Season', foreign_keys=[current_season_id], post_update=True)

    # def fetch_seasons(self):
    #     seasons_data = self.fetch_from_db_or_api(self.id)
    #     for season_data in seasons_data:
    #         season = Season(season_data['id'])
    #         db.session.add(season)

    def __repr__(self):
        return f'<League {self.name}>'


class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Attributes
    name = db.Column(db.String(64), index=False, unique=False)
    total_teams = db.Column(db.Integer, index=False, unique=False)
    year = db.Column(db.Integer, index=False, unique=False)
    season_type = db.Column(db.String(64), index=False, unique=False)
    # Foreign Keys
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), index=True, unique=False)
    draft_id = db.Column(db.Integer, index=False, unique=False)
    # Relationships
    matchups = db.relationship('Matchup', backref='season', lazy='dynamic')
    users = db.relationship('User', backref='season', lazy='dynamic') # many to many
    teams = db.relationship('Team', backref='season', lazy='dynamic')


    # def fetch_matchups(self):
    #     matchups_data = self.fetch_from_db_or_api(self.id)
    #     for matchup_data in matchups_data:
    #         matchup = Matchup(matchup_data['id'])
    #         db.session.add(matchup)
    #
    # def fetch_teams(self):
    #     teams_data = self.fetch_from_db_or_api(self.id)
    #     for team_data in teams_data:
    #         team = Team(team_data['id'])
    #         db.session.add(team)

    def __repr__(self):
        return f'<Season {self.id}>'


class Matchup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Attributes
    matchup_id = db.Column(db.Integer, index=True, unique=False) # season_id + week + matchup_id
    week = db.Column(db.Integer, index=True, unique=False)
    year = db.Column(db.Integer, index=True, unique=False)
    points_for = db.Column(db.Integer, index=False, unique=False)
    points_against = db.Column(db.Integer, index=False, unique=False)
    win = db.Column(db.Boolean, index=False, unique=False)
    loss = db.Column(db.Boolean, index=False, unique=False)
    tie = db.Column(db.Boolean, index=False, unique=False)
    playoff = db.Column(db.Boolean, index=False, unique=False)
    consolation = db.Column(db.Boolean, index=False, unique=False)
    championship = db.Column(db.Boolean, index=False, unique=False)
    # Foreign Keys
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), index=True, unique=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), index=True, unique=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, unique=False)
    opponent_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), index=True, unique=False)
    opponent_owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, unique=False)

    # Relationships

    def __repr__(self):
        return f'<Matchup {self.id}>'




class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Season ID + Roster ID
    # Attributes
    name = db.Column(db.String(64), index=True, unique=False)
    year = db.Column(db.Integer, index=False, unique=False)
    total_wins = db.Column(db.Integer, index=False, unique=False)
    total_losses = db.Column(db.Integer, index=False, unique=False)
    total_ties = db.Column(db.Integer, index=False, unique=False)
    total_points_for = db.Column(db.Integer, index=False, unique=False)
    total_points_against = db.Column(db.Integer, index=False, unique=False)
    total_moves = db.Column(db.Integer, index=False, unique=False)
    total_trades = db.Column(db.Integer, index=False, unique=False)
    is_commish = db.Column(db.Boolean, index=False, unique=False)
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'))
    league_id  = db.Column(db.Integer, db.ForeignKey('league.id'))
    # Relationships
    matchups_as_owner = db.relationship('Matchup', foreign_keys='matchup.team_id', backref='team', lazy='dynamic')
    matchups_as_opponent = db.relationship('Matchup', foreign_keys='matchup.opponent_team_id', backref='opponent_team', lazy='dynamic')
    players = db.relationship('Player', secondary=player_team_association, lazy='subquery',
                              backref=db.backref('teams', lazy=True))
    def __repr__(self):
        return f'<Team {self.name}>'


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Attributes
    first_name = db.Column(db.String(64), index=False, unique=False)
    last_name = db.Column(db.String(64), index=True, unique=False)
    number = db.Column(db.Integer, index=False, unique=False)
    position = db.Column(db.String(64), index=True, unique=False)
    nfl_team = db.Column(db.String(64), index=False, unique=False)
    age = db.Column(db.Integer, index=True, unique=False)
    status = db.Column(db.String(64), index=False, unique=False)
    years_exp = db.Column(db.Integer, index=True, unique=False)
    weight = db.Column(db.Integer, index=False, unique=False)
    height = db.Column(db.Integer, index=False, unique=False)
    injury_status = db.Column(db.Boolean, index=False, unique=False)





# class NflState(db.Model):
#     week = db.Column(db.Integer, primary_key=True)
#     season = db.Column(db.Integer, index=False, unique=False)
#     season_type = db.Column(db.String(64), index=False, unique=False)
