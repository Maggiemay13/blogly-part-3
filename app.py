"""Blogly application."""
from flask import Flask, request, redirect, render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)


with app.app_context():

    db.create_all()


@app.route('/')
def root():
    """Homepage redirects to list of users."""

    return redirect("/users")


@app.route('/users')
def users_index():
    """Show a page with info on all users"""

    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('users/index.html', users=users)


@app.route('/users/new', methods=["GET"])
def users_new_form():
    """Show a form to create a new user"""

    return render_template('users/new.html')


@app.route("/users/new", methods=["POST"])
def users_new():
    """Handle form submission for creating a new user"""

    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url=request.form['image_url'] or None)

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show a page with info on a specific user"""

    user = User.query.get_or_404(user_id)
    return render_template('users/show.html', user=user)


@app.route('/users/<int:user_id>/edit')
def users_edit(user_id):
    """Show a form to edit an existing user"""

    user = User.query.get_or_404(user_id)
    return render_template('users/edit.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=["POST"])
def users_update(user_id):
    """Handle form submission for updating an existing user"""

    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def users_destroy(user_id):
    """Handle form submission for deleting an existing user"""

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")


# -------------------------------------------------------------------------------------
# Post routes

# GET /users/[user-id]/posts/new : Show form to add a post for that user.
@app.route('/users/<int:user_id>/posts/new', methods=["GET"])
def new_post_form(user_id):
    """Show a form to create a new post far a specific user"""

    user = User.query.get_or_404(user_id)
    return render_template('posts/new.html', user=user)

# POST /users/[user-id]/posts/new : Handle add form; add post and redirect to the user detail page.


@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def posts_new(user_id):
    """Handle form submission for creating a new post for a specific user"""

    user = User.query.get_or_404(user_id)
    new_post = Post(title=request.form['title'],
                    content=request.form['content'],
                    created_date=datetime.now(),
                    user_id=user.id)

    db.session.add(new_post)
    db.session.commit()

    return redirect(f"/users/{user_id}")


@app.route('/posts/<int:post_id>')
def posts_show(post_id):
    """Show a page with the info on a specific post """

    post = Post.query.get_or_404(post_id)
    return render_template('/posts/show.html', post=post)
# post=post is passing the retreived 'post' object to the template when rendering it


@app.route('/posts/<int:post_id>/edit')
def posts_edit(post_id):
    """Show a form to edit an existing post"""

    post = Post.query.get_or_404(post_id)
    return render_template('posts/edit.html', post=post)


@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def posts_update(post_id):
    """Handle form submission for updating an existing post"""

    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']

    db.session.add(post)
    db.session.commit()

    return redirect(f"/users/{post.user_id}")


@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def posts_destroy(post_id):
    """Handle form submission for deleting an existing post"""

    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{post.user_id}")


# -------------------------------------------------------------------------------------------------------------
# tags route


@app.route('/tags')
def tags_index():
    """show a page with infor on all tags"""

    tags = Tag.query.all()
    return render_template('tags/index.html', tags=tags)

# handeling the GET request


@app.route('/tags/new')
def tags_new_form():
    """show form to create a new tag"""

    posts = Post.query.all()
    return render_template('tags/new.html', posts=posts)

#  handeling the post request


@app.route("/tags/new", methods=["POST"])
def tags_new():
    """Handel form submission for creating a new tag"""

    # Extract the selected post IDs from the form
    post_ids = [int(num) for num in request.form.getlist("posts")]

    # Query the selected posts from the database
    posts = Post.query.filter(Post.id.in_(post_ids)).all()

    # Create a new Tag object with the provided name and accociated posts
    new_tag = Tag(name=request.form['name'], posts=posts)

    # Add the new_tag to the database session
    db.session.add(new_tag)

    # Commit the changes to the database
    db.session.commit()

    # Redirect the user to thr "/tags" page after creating the tag
    return redirect("/tags")


@app.route('/tags/<int:tag_id>')
def tags_show(tag_id):
    """Show a page with info on a specific tag"""

    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags/show.html', tag=tag)


@app.route('/tags/<int:tag_id>/edit')
def tags_edit_form(tag_id):
    """Show for to edit an exsisting tag"""

    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template('/tags/edit.html', tag=tag, posts=posts)


@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def tags_edit(tag_id):
    """Handel form submission for updating an existing tag"""

    # Retrieve the tag with the givin tag_id from the database, or return a 404
    tag = Tag.query.get_or_404(tag_id)

    # Update the name of the tag with the value provided in the form
    tag.name = request.form['name']

    # Extract the selected post IDs from the form
    post_ids = [int(num) for num in request.form.getlist("posts")]

    # Query the selected posts from the database
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    # Add the updated tag to the database session
    db.session.add(tag)

    # commit changes to database
    db.session.commit()

    # Redirect the user to the /tags page after editing the tag
    return redirect("/tags")


@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def tags_destroy(tag_id):
    """Handle form submission for deleting an existing tag"""

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()

    return redirect("/tags")
