"""User model tests."""

import os
from sqlalchemy.exc import IntegrityError
from unittest import TestCase
from flask_bcrypt import Bcrypt

from models import db, User, DEFAULT_IMG_URL

# set up test database before importing app because
# app already connected to a database
os.environ['DATABASE_URL'] = "postgresql:///craft_app_test"

from app import app

bcrypt = Bcrypt()

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        hashed_password = (bcrypt
            .generate_password_hash("password")
            .decode('UTF-8')
        )

        u1 = User(
            username="u1",
            email="u1@email.com",
            password=hashed_password,
            image_url=None,
        )

        u2 = User(
            username="u2",
            email="u2@email.com",
            password=hashed_password,
            image_url=None,
        )

        db.session.add_all([u1, u2])
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Test user instance initialized correctly."""

        u1 = User.query.get(self.u1_id)

        self.assertEqual(len(u1.projects), 0)
        self.assertEqual(len(u1.following), 0)
        self.assertEqual(len(u1.followers), 0)
        self.assertEqual(len(u1.requests_received), 0)
        self.assertEqual(len(u1.requests_made), 0)

    # #################### Signup tests

    def test_valid_signup(self):
        """Test User class method signup with valid inputs"""

        user = User.signup(
            username='new_user',
            email='new_user@email.com',
            image_url=None,
            password='password'
        )

        db.session.add(user)
        db.session.commit()

        self.assertIsInstance(user, User)
        self.assertEqual(user.email, 'new_user@email.com')
        self.assertEqual(user.image_url, DEFAULT_IMG_URL)
        self.assertNotEqual(user.password, 'password')
        self.assertEqual(user.private, False)
        # Bcrypt strings should start with $2b$
        self.assertTrue(user.password.startswith("$2b$"))

    def test_invalid_signup_bad_username(self):
        """Test User class method, signup, with bad username"""

        with self.assertRaises(IntegrityError):
            user = User.signup(
                username='u1',
                email='new_user@email.com',
                image_url=None,
                password='password'
            )

            db.session.add(user)
            db.session.commit()

    def test_invalid_signup_bad_email(self):
        """Test User class method signup with bad username"""

        with self.assertRaises(IntegrityError):
            user = User.signup(
                username='new_user',
                email='u1@email.com',
                image_url=None,
                password='password'
            )

            db.session.add(user)
            db.session.commit()

    # #################### Authentication tests

    def test_valid_login(self):
        """Test User class method, login, with valid credentials"""

        user = User.login('u1', 'password')

        u1 = User.query.get(self.u1_id)

        self.assertEqual(user, u1)

    def test_invalid_login_bad_username(self):
        """Test User class method, login, with bad username"""

        user = User.login('bad_user', 'password')

        self.assertFalse(user)

    def test_invalid_login_bad_password(self):
        """Test User class method, login, with bad password"""

        user = User.login('u1', 'bad_password')

        self.assertFalse(user)

    # #################### Follow tests

    def test_follows(self):
        """Test follows table/user <--> user relationship working."""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.followers.append(u2)
        db.session.commit()

        self.assertEqual(u1.followers, [u2])
        self.assertEqual(u2.followers, [])
        self.assertEqual(u1.following, [])
        self.assertEqual(u2.following, [u1])

    def test_is_following(self):
        """Test User class method, is_following."""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.followers.append(u2)
        db.session.commit()

        self.assertFalse(u1.is_following(u2))
        self.assertTrue(u2.is_following(u1))

    def test_is_followed_by(self):
        """Test User class method, is_followed_by."""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.followers.append(u2)
        db.session.commit()

        self.assertTrue(u1.is_followed_by(u2))
        self.assertFalse(u2.is_followed_by(u1))

    # #################### Request tests

    def test_requests(self):
        """Test requests table/user <--> user relationship working."""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.requests_received.append(u2)
        db.session.commit()

        self.assertEqual(u1.requests_received, [u2])
        self.assertEqual(u2.requests_received, [])
        self.assertEqual(u1.requests_made, [])
        self.assertEqual(u2.requests_made, [u1])