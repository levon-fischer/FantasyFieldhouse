from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import current_user, login_user, logout_user, login_required

from fantasyApp import bcrypt, db
from fantasyApp.models import User, Post
from fantasyApp.users.forms import (
    RegistrationForm,
    LoginForm,
    UpdateAccountForm,
    RequestResetForm,
    ResetPasswordForm,
)
from fantasyApp.users.utils import save_picture, send_reset_email
from fantasyApp.sleeper_data.users import NewUser
from fantasyApp.sleeper_data.leagues import check_for_new_leagues


users = Blueprint("users", __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        # Create a new user or register an existing user
        user_id = NewUser(form.username.data, form.email.data, hashed_password).user_id
        # Build out the user's profile by adding all their data to the database
        check_for_new_leagues(user_id)
        flash(f"Your account has been created! You are now able to log in", "success")
        return redirect(url_for("users.login"))
    return render_template("register.html", title="Register", form=form)


# @users.route("/register", methods=["GET", "POST"])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for("main.home"))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
#             "utf-8"
#         )
#         # Create a new user
#         user_id = register_user(form.username.data, form.email.data, hashed_password)
#         return redirect(url_for("users.build_profile", user_id=user_id))
#     return render_template("register.html", title="Register", form=form)


# @users.route("/register/<string:user_id>", methods=["GET", "POST"])
# def build_profile(user_id):
#     if current_user.is_authenticated:
#         return redirect(url_for("main.home"))
#     check_for_new_leagues.apply_async(args=[user_id])
#     flash(f"Your account has been created! You are now able to log in", "success")
#     return redirect(url_for("users.login"))
#     return render_template("build_profile.html", title="Build Profile")


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")  # Get the next page if it exists
            flash(f"Welcome back {user.username}!", "success")
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", title="Login", form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)  # Save the picture
            current_user.image_file = picture_file  # Update the image file
        current_user.username = form.username.data  # Update the username
        current_user.email = form.email.data  # Update the email
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("users.account"))
    elif request.method == "GET":
        form.username.data = (
            current_user.username
        )  # Populate the form with the current username
        form.email.data = current_user.email  # Populate the form with the current email
    image_file = url_for("static", filename="profile_pics/" + current_user.image_file)
    return render_template(
        "account.html", title="Account", image_file=image_file, form=form
    )


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(
        username=username
    ).first_or_404()  # Get the user or return 404
    posts = (
        Post.query.filter_by(author=user)
        .order_by(Post.date_posted.desc())
        .paginate(page=page, per_page=5)
    )
    return render_template("user_posts.html", posts=posts, user=user)


@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RequestResetForm()  # Create a new form
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()  # Get the user
        send_reset_email(user)  # Send the reset email
        flash(
            "An email has been sent with instructions to reset your password.", "info"
        )
        return redirect(url_for("users.login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("users.reset_request"))
    form = ResetPasswordForm()  # Create a new form
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user.password = hashed_password  # Update the password
        db.session.commit()
        flash(f"Your has been updated! You are now able to log in", "success")
        return redirect(url_for("users.login"))
    return render_template("reset_token.html", title="Reset Password", form=form)
