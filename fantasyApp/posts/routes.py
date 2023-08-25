from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from fantasyApp import db
from fantasyApp.models import Post
from fantasyApp.posts.forms import PostForm

posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():  # If the form is valid
        post = Post(
            title=form.title.data, content=form.content.data, author=current_user
        )  # Create a new post
        db.session.add(post)  # Add the post to the database
        db.session.commit()  # Commit the changes
        flash("Your post has been created!", "success")
        return redirect(url_for("main.home"))
    return render_template("create_post.html", title="New Post",
                           form=form, legend="New Post")

@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)  # Get the post or return 404
    return render_template("post.html", title=post.title, post=post)


@posts.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)  # Get the post or return 404
    if post.author != current_user:  # If the author is not the current user
        abort(403)  # Return 403
    form = PostForm()  # Create a new form
    if form.validate_on_submit():  # If the form is valid
        post.title = form.title.data  # Update the title
        post.content = form.content.data  # Update the content
        db.session.commit()  # Commit the changes
        flash("Your post has been updated!", "success")
        return redirect(url_for("posts.post", post_id=post.id))
    elif request.method == "GET":  # If the request is a GET request
        form.title.data = post.title  # Populate the form with the current title
        form.content.data = post.content  # Populate the form with the current content
    return render_template("create_post.html", title="Update Post",
                           form=form, legend="Update Post")


@posts.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)  # Get the post or return 404
    if post.author != current_user:  # If the author is not the current user
        abort(403)  # Return 403
    db.session.delete(post)  # Delete the post
    db.session.commit()  # Commit the changes
    flash("Your post has been deleted!", "success")
    return redirect(url_for("main.home"))