from unittest import TestCase

from app import app
from models import db, User, Post

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_blogly'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
with app.app_context():
    db.drop_all()
    db.create_all()


class BloglyTestCase(TestCase):

    def create_app(self):
        """Create the Flask app instance."""

        return app

    def setUp(self):
        """Set up the test database and create all tables."""

        db.create_all()

    def tearDown(self):
        """Remove all tables from the test database."""

        db.session.remove()
        db.drop_all()

    def test_user_full_name(self):
        """Test the full_name property of the User model."""

        # Create a test user
        user = User(first_name="John", last_name="Doe", image_url="test_url")

        # Assert the full name is correct
        self.assertEqual(user.full_name, "John Doe")

    def test_create_post(self):
        """Test creating a new post."""

        # Create a test user
        user = User(first_name="John", last_name="Doe", image_url="test_url")
        db.session.add(user)
        db.session.commit()

        # Create a test post
        post = Post(title="Test Post", content="This is a test post.",
                    created_date=datetime.now(), user_id=user.id)

        # Add the post to the database
        db.session.add(post)
        db.session.commit()

        # Retrieve the post from the database
        post_from_db = Post.query.get(post.id)

        # Assert the post is in the database
        self.assertIsNotNone(post_from_db)
        self.assertEqual(post_from_db.title, "Test Post")
        self.assertEqual(post_from_db.content, "This is a test post.")
        self.assertEqual(post_from_db.user_id, user.id)
