import os
import secrets

from PIL import Image
from flask import url_for, current_app
from flask_mail import Message

from fantasyApp import mail


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)  # Generate a random hex
    _, f_ext = os.path.splitext(
        form_picture.filename
    )  # Get the file name and extension
    picture_fn = random_hex + f_ext  # Create a new file name
    picture_path = os.path.join(
        current_app.root_path, "static/profile_pics", picture_fn
    )  # Create a path to save the picture
    output_size = (125, 125)  # Set the output size
    i = Image.open(form_picture)  # Open the picture
    i.thumbnail(output_size)  # Resize the picture
    i.save(picture_path)  # Save the picture to the path
    return picture_fn  # Return the picture file name


def send_reset_email(user):
    token = user.get_reset_token()  # Get the reset token
    msg = Message(
        "Password Reset Request", sender="noreply@demo.com", recipients=[user.email]
    )
    msg.body = f"""To reset your password, visit the following link: {url_for('users.reset_token', token=token, _external=True)}

    If you did not make this request then simply ignore this email and no changes will be made.
    """
    mail.send(msg)