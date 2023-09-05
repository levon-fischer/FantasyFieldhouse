from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from sqlalchemy import func
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from fantasyApp.models import User
from fantasyApp.sleeper_data.utils import SleeperAPI


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=30)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter(
            func.lower(User.username) == func.lower(username.data)
        ).first()
        if (
            user and user.registered
        ):  # If the user exists in our database and they are registered
            raise ValidationError(
                "This username is already claimed on Fantasy Fieldhouse"
            )
        else:
            user_data = SleeperAPI.fetch_user(username.data)
            if user_data is None:
                raise ValidationError("This username does not exist on Sleeper")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is already taken. Please choose another.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class UpdateAccountForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=30)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    picture = FileField(
        "Update Profile Picture", validators=[FileAllowed(["jpg", "png"])]
    )
    submit = SubmitField("Update")

    def validate_username(self, username):
        if (
            username.data != current_user.username
        ):  # If the username is different than the current username
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    "That username is already taken. Please choose another."
                )

    def validate_email(self, email):
        if (
            email.data != current_user.email
        ):  # If the email is different than the current email
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    "That email is already taken. Please choose another."
                )


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                "There is no account with that email. You must register first."
            )


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")
