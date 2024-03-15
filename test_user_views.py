"""User View tests."""

import os
from unittest import TestCase
from models import db, User, DEFAULT_IMG_URL

# set up test database before importing app because
# app already connected to a database
os.environ['DATABASE_URL'] = "postgresql:///craft_app_test"

from app import app, CURR_USER_KEY

db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

NONEXISTENT_USER_ID = 0


class UserBaseViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup('u1', 'u1@email.com', None, 'password')
        u2 = User.signup('u2', 'u2@email.com', None, 'password')
        u3 = User.signup('u3', 'u3@email.com', None, 'password')
        u4 = User.signup('u4', 'u4@email.com', None, 'password')

        db.session.add_all([u1, u2, u3, u4])
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id
        self.u3_id = u3.id
        self.u4_id = u4.id

    def tearDown(self):
        db.session.rollback()

class UserListTestCase(UserBaseViewTestCase):
    def test_show_all_users(self):
        """Test user list without search query."""
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            resp = client.get('/users')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing user list', html)
            self.assertIn('u1', html)
            self.assertIn('u2', html)
            self.assertIn('u3', html)
            self.assertIn('u4', html)

    def test_show_all_users_no_authentication(self):
        """Test viewing user list without authenticating."""
        with app.test_client() as client:
            resp = client.get('/users', follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Unauthorized', html)
            self.assertIn('for testing anon home', html)

    def test_show_search_users(self):
        """Test user list with search query."""
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            resp = client.get('/users?q=1')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing user list', html)
            self.assertIn('u1', html)
            self.assertNotIn('u2', html)
            self.assertNotIn('u3', html)
            self.assertNotIn('u4', html)


class UserSignupTestCase(UserBaseViewTestCase):
    def test_signup_page(self):
        """Test signup page"""

        with app.test_client() as client:
            resp = client.get('/signup')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing signup page', html)

    def test_valid_signup(self):
        """Test valid signup"""

        with app.test_client() as client:
            resp = client.post(
                '/signup',
                data={
                    'username': 'new_user',
                    'email': 'new_user@email.com',
                    'image': None,
                    'password': 'password'
                },
                follow_redirects=True
            )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing profile page', html)
            self.assertIn('new_user', html)


    def test_valid_signup_bad_username(self):
        """Test signup with bad username"""

        u1 = User.query.get(self.u1_id)

        with app.test_client() as client:
            resp = client.post(
                '/signup',
                data={
                    'username': u1.username,
                    'email': 'new_user@email.com',
                    'image': None,
                    'password': 'password'
                },
                follow_redirects=True
            )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing signup page', html)
            self.assertIn('Username or email already in use.', html)

    def test_valid_signup_bad_email(self):
        """Test signup with bad email"""

        u1 = User.query.get(self.u1_id)

        with app.test_client() as client:
            resp = client.post(
                '/signup',
                data={
                    'username': 'new_user',
                    'email': u1.email,
                    'image': None,
                    'password': 'password'
                },
                follow_redirects=True
            )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing signup page', html)
            self.assertIn('Username or email already in use.', html)


class UserLoginTestCase(UserBaseViewTestCase):
    def test_login_page(self):
        """Test login page"""

        with app.test_client() as client:
            resp = client.get('/login')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing login page', html)

    def test_valid_login(self):
        """Test logging in with valid credentials"""

        with app.test_client() as client:
            resp = client.post(
                '/login',
                data={
                    'username':'u1',
                    'password': 'password'
                },
                follow_redirects=True
            )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing profile page', html)
            self.assertIn('u1', html)

    def test_invalid_login_bad_username(self):
        """Test logging in with bad username"""

        with app.test_client() as client:
            resp = client.post(
                '/login',
                data={
                    'username':'bad_user',
                    'password': 'password'
                },
                follow_redirects=True
            )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing login page', html)
            self.assertIn('Invalid credentials', html)

    def test_invalid_login_bad_password(self):
        """Test logging in with bad password"""

        with app.test_client() as client:
            resp = client.post(
                '/login',
                data={
                    'username':'u1',
                    'password': 'bad_password'
                },
                follow_redirects=True
            )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing login page', html)
            self.assertIn('Invalid credentials', html)


class UserLogoutTestCase(UserBaseViewTestCase):
    def test_successful_logout(self):
        """Test successful user logout"""
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            resp = client.post('/logout', follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing login page', html)
            self.assertIn('Logged out', html)

    def test_unauthorized_logout(self):
        """Test unathorized user logout"""
        with app.test_client() as client:

            resp = client.post('/logout', follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing anon home', html)
            self.assertIn('Unauthorized', html)


class UserProfileTestCase(UserBaseViewTestCase):
    def test_profile_page(self):
        """Test user profile page."""
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            resp = client.get('/profile')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing profile page', html)
            self.assertIn('u1', html)

    def test_unathorized_profile_page(self):
        """Test unauthorized user profile page access."""
        with app.test_client() as client:

            resp = client.get('/profile', follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Unauthorized', html)
            self.assertIn('for testing anon home', html)


class UserSettingsTestCase(UserBaseViewTestCase):
    def test_get_settings_page(self):
        """Test user settings page."""
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            resp = client.get('/settings')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing settings page', html)

    def test_unathorized_get_settings_page(self):
        """Test unauthorized user setting page access."""
        with app.test_client() as client:
            resp = client.get('/settings', follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Unauthorized', html)
            self.assertIn('for testing anon home', html)

    def test_post_settings_page(self):
        """Test editing user settings."""
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            resp = client.post(
                '/settings',
                data={
                    'username': 'edited_u1',
                    'email': 'edited@email.com',
                    'image_url': None
                },
                )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing settings page', html)
            self.assertIn('Changes saved', html)
            self.assertIn('edited_u1', html)
            self.assertIn('edited@email.com', html)
            self.assertIn(DEFAULT_IMG_URL, html)

    def test_unauthorized_post_settings_page(self):
        """Test unauthorized editing user settings."""
        with app.test_client() as client:
            resp = client.post(
                '/settings',
                data={
                    'username': 'edited_u1',
                    'email': 'edited@email.com',
                    'image_url': None
                    },
                follow_redirects=True
                )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Unauthorized', html)
            self.assertIn('for testing anon home', html)


class UserNotificationsTestCase(UserBaseViewTestCase):
    def test_notifications_page(self):
        """Test notifications page."""
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.requests_received.append(u2)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            resp = client.get('/notifications')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing notifications page', html)
            self.assertIn('u2', html)

    def test_unathorized_notifications_page(self):
        """Test unauthorized notifications page access."""

        with app.test_client() as client:
            resp = client.get('/notifications', follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing anon home', html)
            self.assertIn('Unauthorized', html)


class UserPageTestCase(UserBaseViewTestCase):
    def test_own_user_page(self):
        """Test viewing own user page"""

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            resp = client.get(f'/users/{self.u1_id}')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing profile page', html)
            self.assertIn('u1', html)
            self.assertIn('Add Project', html)
            self.assertIn('Log time', html)
            self.assertNotIn('formaction="/users/{{user.id}}/follow"', html)

    def test_other_user_page(self):
        """Test viewing other's user page"""

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            resp = client.get(f'/users/{self.u2_id}')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing profile page', html)
            self.assertIn('u2', html)
            self.assertNotIn('Add Project', html)
            self.assertNotIn('Log time', html)
            self.assertIn('for testing follow button', html)

    def test_unauthorized_user_page(self):
        """Test unauthorized access to user page"""

        with app.test_client() as client:

            resp = client.get(f'/users/{self.u1_id}', follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing anon home', html)
            self.assertIn('Unauthorized', html)

    def test_private_user_page(self):
        """Test private user page"""

        u2 = User.query.get(self.u2_id)
        u2.private = True
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            resp = client.get(f'/users/{self.u2_id}')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Account is private', html)

    def test_authorized_private_user_page(self):
        """Test private user page of user being followed"""

        u2 = User.query.get(self.u2_id)
        u2.private = True
        db.session.commit()

        u1 = User.query.get(self.u1_id)
        u1.following.append(u2)

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            resp = client.get(f'/users/{self.u2_id}')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing profile page', html)
            self.assertNotIn('Account is private', html)

    # def test_nonexistent_user_page(self):
    #     """Test unauthorized access to user page"""

    #     with app.test_client() as client:

    #         print('*******************', f'/users/{NONEXISTENT_USER_ID}')

    #         resp = client.get(f'/users/{NONEXISTENT_USER_ID}', follow_redirects=True)

    #         self.assertEqual(resp.status_code, 404)


class UserPrivateTestCase(UserBaseViewTestCase):
    def test_private_user(self):
        """Test privating user"""

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            resp = client.post('/settings/private', follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Account now private', html)
            self.assertIn('for testing settings page', html)

    def test_unathorized_private_user(self):
        """Test unauthorized privating of user"""

        with app.test_client() as client:
            resp = client.post('/settings/private', follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Unauthorized', html)
            self.assertIn('for testing anon home', html)

    def test_unprivate_user(self):
        """Test unprivating user"""

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            resp = client.post('/settings/unprivate', follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Account now public', html)
            self.assertIn('for testing settings page', html)

    def test_unathorized_unprivate_user(self):
        """Test unauthorized unprivating of user"""

        with app.test_client() as client:
            resp = client.post('/settings/unprivate', follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Unauthorized', html)
            self.assertIn('for testing anon home', html)

class UserFollowingPageTestCase(UserBaseViewTestCase):
    def test_user_following_page(self):
        """Test user following page"""

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            u1 = User.query.get(self.u1_id)
            u2 = User.query.get(self.u2_id)

            u1.following.append(u2)
            db.session.commit()

            resp = client.get(f'/users/{self.u1_id}/following')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing following page', html)
            self.assertIn('u2', html)

    def test_unathorized_user_following_page(self):
        """Test unauthorized access to user following page"""

        with app.test_client() as client:
            resp = client.get(
                f'/users/{self.u1_id}/following',
                follow_redirects=True
            )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Unauthorized', html)
            self.assertIn('for testing anon home', html)

    # def test_nonexistent_user_following_page(self):
    #     """Test access to nonexistent user's following page"""

    #     with app.test_client() as client:
    #         resp = client.get(
    #             f'/users/{NONEXISTENT_USER_ID}/following',
    #             follow_redirects=True
    #         )

    #         self.assertEqual(resp.status_code, 404)

class UserFollowersPageTestCase(UserBaseViewTestCase):
    def test_user_followers_page(self):
        """Test user followers page"""

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            u1 = User.query.get(self.u1_id)
            u2 = User.query.get(self.u2_id)

            u1.followers.append(u2)
            db.session.commit()

            resp = client.get(f'/users/{self.u1_id}/followers')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing followers page', html)
            self.assertIn('u2', html)

    def test_unathorized_user_followers_page(self):
        """Test unauthorized access to user followers page"""

        with app.test_client() as client:
            resp = client.get(
                f'/users/{self.u1_id}/followers',
                follow_redirects=True
            )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Unauthorized', html)
            self.assertIn('for testing anon home', html)

    # def test_nonexistent_user_followers_page(self):
    #     """Test access to nonexistent user's followers page"""

    #     with app.test_client() as client:
    #         resp = client.get(
    #             f'/users/{NONEXISTENT_USER_ID}/followers',
    #             follow_redirects=True
    #         )

    #         self.assertEqual(resp.status_code, 404)


class UserDeleteTestCase(UserBaseViewTestCase):
    def test_user_delete(self):
        """Test deleting user"""

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            resp = client.post(
                f'/users/delete',
                follow_redirects=True
                )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('for testing signup page', html)
            self.assertIn('User deleted', html)

    def test_unathorized_user_delete(self):
        """Test unauthorized deleting user"""

        with app.test_client() as client:
            resp = client.post(
                f'/users/delete',
                follow_redirects=True
                )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Unauthorized', html)
            self.assertIn('for testing anon home', html)

class UserFollowTestCase(UserBaseViewTestCase):
    def test_follow_public_user(self):
        """Test follow public user"""

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            resp = client.post(
                f'/users/{self.u2_id}/follow',
                data={'came_from': f'/users'},
                follow_redirects=True
                )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Now following', html)
            self.assertIn('Unfollow', html)
            self.assertIn('for testing user list', html)

    def test_unauthorized_follow_user(self):
        """Test unauthorized follow user"""

        with app.test_client() as client:
            resp = client.post(
                f'/users/{self.u2_id}/follow',
                data={'came_from': f'/users/{self.u2_id}'},
                follow_redirects=True
                )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Unauthorized', html)
            self.assertIn('for testing anon home', html)

    def test_follow_private_user(self):
        """Test follow private user"""

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            u2 = User.query.get(self.u2_id)
            u2.private = True
            db.session.commit()

            resp = client.post(
                f'/users/{self.u2_id}/follow',
                data={'came_from': f'/users/{self.u2_id}'},
                follow_redirects=True
                )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Request sent to', html)
            self.assertIn('Requested', html)
            self.assertIn('for testing profile page', html)

    def test_unauthorized_follow_private_user(self):
        """Test unauthorized follow private user"""

        with app.test_client() as client:
            u2 = User.query.get(self.u2_id)
            u2.private = True
            db.session.commit()

            resp = client.post(
                f'/users/{self.u2_id}/follow',
                data={'came_from': f'/users/{self.u2_id}'},
                follow_redirects=True
                )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Unauthorized', html)
            self.assertIn('for testing anon home', html)

    def test_unauthorized_follow_private_user(self):
        """Test unauthorized follow private user"""

        with app.test_client() as client:
            u2 = User.query.get(self.u2_id)
            u2.private = True
            db.session.commit()

            resp = client.post(
                f'/users/{self.u2_id}/follow',
                data={'came_from': f'/users/{self.u2_id}'},
                follow_redirects=True
                )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Unauthorized', html)
            self.assertIn('for testing anon home', html)

class UserRequestTestCase(UserBaseViewTestCase):
    def test_cancel_follow_request(self):
        """Test cancel follow request"""

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            u1 = User.query.get(self.u1_id)
            u2 = User.query.get(self.u2_id)

            u1.requests_made.append(u2)
            db.session.commit()

            resp = client.post(
                f'/users/{self.u2_id}/cancel_request',
                data={'came_from': f'/users/{self.u2_id}'},
                follow_redirects=True
                )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Canceled follow request', html)
            self.assertIn('for testing profile page', html)
            self.assertIn('follow', html)

    def test_unauthorized_cancel_follow_request(self):
        """Test unauthorized cancel follow request"""

        with app.test_client() as client:
            u1 = User.query.get(self.u1_id)
            u2 = User.query.get(self.u2_id)

            u1.requests_made.append(u2)
            db.session.commit()

            resp = client.post(
                f'/users/{self.u2_id}/cancel_request',
                data={'came_from': f'/users/{self.u2_id}'},
                follow_redirects=True
                )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Unauthorized', html)
            self.assertIn('for testing anon home', html)

    def test_confirm_follow_request(self):
        """Test confirming follow request"""
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            u1 = User.query.get(self.u1_id)
            u2 = User.query.get(self.u2_id)

            u2.requests_made.append(u1)
            db.session.commit()

            resp = client.post(f'requests/{u2.id}/confirm', follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'{u2.username} is following you now', html)
            self.assertIn('for testing notifications page', html)

    def test_unauthorized_confirm_follow_request(self):
        """Test unauthorized confirmation of follow request"""
        with app.test_client() as client:
            u1 = User.query.get(self.u1_id)
            u2 = User.query.get(self.u2_id)

            u2.requests_made.append(u1)
            db.session.commit()

            resp = client.post(f'requests/{u2.id}/confirm', follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'Unauthorized', html)
            self.assertIn('for testing anon home', html)

    def test_delete_follow_request(self):
        """Test deleting follow request"""
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1_id

            u1 = User.query.get(self.u1_id)
            u2 = User.query.get(self.u2_id)

            u2.requests_made.append(u1)
            db.session.commit()

            resp = client.post(f'requests/{u2.id}/delete', follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'Deleted follow request', html)
            self.assertIn('for testing notifications page', html)

    def test_unauthorized_delete_follow_request(self):
        """Test unauthorized deletion of follow request"""
        with app.test_client() as client:
            u1 = User.query.get(self.u1_id)
            u2 = User.query.get(self.u2_id)

            u2.requests_made.append(u1)
            db.session.commit()

            resp = client.post(f'requests/{u2.id}/delete', follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'Unauthorized', html)
            self.assertIn('for testing anon home', html)


