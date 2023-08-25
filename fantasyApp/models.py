from datetime import datetime
from itsdangerous.timed import TimedSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
from flask import current_app
from fantasyApp import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=False, nullable=False)
    registered = db.Column(db.Boolean, index=True, unique=False, default=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    image_file = db.Column(
        db.String(20), index=False, unique=False, nullable=False, default="default.jpg"
    )
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship("Post", backref="author", lazy="dynamic")

    # display_name = db.Column(db.String(64), index=True, unique=True)
    # avatar = db.Column(db.String(64), index=True, unique=True)
    # matchups = db.relationship('Matchup', backref='user', lazy='dynamic')
    # total_wins = db.Column(db.Integer, index=True, unique=False)
    # total_losses = db.Column(db.Integer, index=True, unique=False)
    # total_ties = db.Column(db.Integer, index=True, unique=False)
    # total_points_for = db.Column(db.Integer, index=True, unique=False)
    # total_points_against = db.Column(db.Integer, index=True, unique=False)
    # total_moves = db.Column(db.Integer, index=True, unique=False)
    # total_trades = db.Column(db.Integer, index=True, unique=False)

    # def __init__(self, username):
    #     self.username = username

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
    title = db.Column(db.String(100), index=True, unique=False, nullable=False)
    date_posted = db.Column(
        db.DateTime, index=False, unique=False, nullable=False, default=datetime.utcnow
    )
    content = db.Column(db.Text, index=False, unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"<Post {self.title}, {self.date_posted}>"


# class League(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     current_season_id = db.Column(db.Integer, db.ForeignKey('season.id'), index=True, unique=True)
#     seasons = db.relationship('Season', backref='league', lazy='select')
#     name = db.Column(db.String(64), index=False, unique=False)
#     total_teams = db.Column(db.Integer, index=False, unique=False)
#     num_seasons = db.Column(db.Integer, index=False, unique=False)
#     users = db.relationship('User', backref='league', lazy='dynamic')
#
#     def __init__(self, league_id):
#         self.id = league_id
#         self.related_league_ids = self.all_league_ids()
#         self.fetch_seasons()
#
#     def fetch_seasons(self):
#         seasons_data = self.fetch_from_db_or_api(self.id)
#         for season_data in seasons_data:
#             season = Season(season_data['id'])
#             db.session.add(season)
#
#     def __repr__(self):
#         return f'<User'
#
#
# class Season(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     matchups = db.relationship('Matchup', backref='season', lazy='dynamic')
#     users = db.relationship('User', backref='season', lazy='dynamic')
#     teams = db.relationship('Team', backref='season', lazy='dynamic')
#
#     def __init__(self, league_id):
#         self.id = league_id
#         self.fetch_matchups()
#
#     def fetch_matchups(self):
#         matchups_data = self.fetch_from_db_or_api(self.id)
#         for matchup_data in matchups_data:
#             matchup = Matchup(matchup_data['id'])
#             db.session.add(matchup)
#
#     def fetch_teams(self):
#         teams_data = self.fetch_from_db_or_api(self.id)
#         for team_data in teams_data:
#             team = Team(team_data['id'])
#             db.session.add(team)
#
#     def __repr__(self):
#         return f'<Season {self.id}>'
#
#
# class Matchup(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     matchup_id = db.Column(db.Integer, index=True, unique=False)
#     week = db.Column(db.Integer, index=True, unique=False)
#     year = db.Column(db.Integer, index=True, unique=False)
#     season_id = db.Column(db.Integer, db.ForeignKey('season.id'))
#     team_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, unique=False)
#     opponent_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, unique=False)
#     points_for = db.Column(db.Integer, index=False, unique=False)
#     points_against = db.Column(db.Integer, index=False, unique=False)
#     win = db.Column(db.Boolean, index=False, unique=False)
#     loss = db.Column(db.Boolean, index=False, unique=False)
#     tie = db.Column(db.Boolean, index=False, unique=False)
#     playoff = db.Column(db.Boolean, index=False, unique=False)
#     consolation = db.Column(db.Boolean, index=False, unique=False)
#     championship = db.Column(db.Boolean, index=False, unique=False)
#
#     def __repr__(self):
#         return f'<Matchup {self.id}>'
#
#
# class Team(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64), index=True, unique=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     season_id = db.Column(db.Integer, db.ForeignKey('season.id'))
#     year = db.Column(db.Integer, index=False, unique=False)
#     matchups = db.relationship('Matchup', backref='team', lazy='dynamic')
#     players = db.relationship('Player', backref='team', lazy='dynamic')
#     total_wins = db.Column(db.Integer, index=False, unique=False)
#     total_losses = db.Column(db.Integer, index=False, unique=False)
#     total_ties = db.Column(db.Integer, index=False, unique=False)
#     total_points_for = db.Column(db.Integer, index=False, unique=False)
#     total_points_against = db.Column(db.Integer, index=False, unique=False)
#     total_moves = db.Column(db.Integer, index=False, unique=False)
#     total_trades = db.Column(db.Integer, index=False, unique=False)
#
#     def __repr__(self):
#         return f'<Team {self.name}>'
#
#
# class Player(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     team_id = db.Column(db.Integer, db.ForeignKey('team.id'), index=True, unique=False)
#     first_name = db.Column(db.String(64), index=False, unique=False)
#     last_name = db.Column(db.String(64), index=True, unique=False)
#     number = db.Column(db.Integer, index=False, unique=False)
#     position = db.Column(db.String(64), index=True, unique=False)
#     nfl_team = db.Column(db.String(64), index=False, unique=False)
#     age = db.Column(db.Integer, index=True, unique=False)
#     status = db.Column(db.String(64), index=False, unique=False)
#     years_exp = db.Column(db.Integer, index=True, unique=False)
#     weight = db.Column(db.Integer, index=False, unique=False)
#     height = db.Column(db.Integer, index=False, unique=False)
#     injury_status = db.Column(db.Boolean, index=False, unique=False)
#
#
# class NflState(db.Model):
#     week = db.Column(db.Integer, primary_key=True)
#     season = db.Column(db.Integer, index=False, unique=False)
#     season_type = db.Column(db.String(64), index=False, unique=False)
