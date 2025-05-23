from tests.base_test import BaseTestCase, db
from app.models import User
from flask import url_for

class TestAuthRoutes(BaseTestCase):

    def test_registration_page_loads(self):
        response = self.client.get(url_for('auth.register'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_login_page_loads(self):
        response = self.client.get(url_for('auth.login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data)

    def test_user_registration_success(self):
        response = self.client.post(
            url_for('auth.register'),
            data=dict(username="newuser", email="new@example.com", password="newpassword", password2="newpassword"),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Should redirect to login
        self.assertIn(b'Congratulations, you are now a registered user!', response.data)
        user = User.query.filter_by(username="newuser").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "new@example.com")

    def test_user_registration_duplicate_username(self):
        self.create_test_user(username="existinguser", email="exists@example.com", password="password")
        response = self.client.post(
            url_for('auth.register'),
            data=dict(username="existinguser", email="new2@example.com", password="password", password2="password"),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please use a different username.', response.data)

    def test_user_registration_duplicate_email(self):
        self.create_test_user(username="anotheruser", email="original@example.com", password="password")
        response = self.client.post(
            url_for('auth.register'),
            data=dict(username="newuser3", email="original@example.com", password="password", password2="password"),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please use a different email address.', response.data)

    def test_user_login_success(self):
        # User is created in BaseTestCase.setUp
        response = self.login(username="testuser", password="password")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hi, testuser!', response.data) # Assuming index shows username
        self.assertIn(b'Logout', response.data)
        self.assertNotIn(b'Login', response.data)

    def test_user_login_invalid_username(self):
        response = self.login(username="wronguser", password="password")
        self.assertEqual(response.status_code, 200) # Stays on login page
        self.assertIn(b'Invalid username or password', response.data)
        self.assertIn(b'Sign In', response.data) # Still on login page

    def test_user_login_invalid_password(self):
        # User is created in BaseTestCase.setUp
        response = self.login(username="testuser", password="wrongpassword")
        self.assertEqual(response.status_code, 200) # Stays on login page
        self.assertIn(b'Invalid username or password', response.data)
        self.assertIn(b'Sign In', response.data) # Still on login page

    def test_user_logout(self):
        self.login(username="testuser", password="password") # Log in first
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hi, Guest!', response.data) # Assuming index shows Guest
        self.assertIn(b'Login', response.data)
        self.assertNotIn(b'Logout', response.data)

    def test_password_reset_request_page_loads(self):
        response = self.client.get(url_for('auth.reset_password_request'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Reset Password', response.data)

    def test_password_reset_request_submit(self):
        # User is created in BaseTestCase.setUp
        response = self.client.post(
            url_for('auth.reset_password_request'),
            data=dict(email="test@example.com"),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Redirects to login
        self.assertIn(b'Check your email for the instructions to reset your password', response.data)
        # Further testing would require email mocking and token verification,
        # which is beyond the current app's simple implementation.

    def test_password_reset_request_unknown_email(self):
        response = self.client.post(
            url_for('auth.reset_password_request'),
            data=dict(email="unknown@example.com"),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Redirects to login
        # To avoid email enumeration, the message is the same
        self.assertIn(b'Check your email for the instructions to reset your password', response.data)

    def test_reset_password_page_loads_with_placeholder_token(self):
        # This tests the route structure, not actual token validity
        # In the current app, the token is a placeholder (user ID)
        user = User.query.filter_by(username="testuser").first()
        response = self.client.get(url_for('auth.reset_password', token=str(user.id)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Reset Your Password', response.data)

    def test_reset_password_submit_with_placeholder_token(self):
        user = User.query.filter_by(username="testuser").first()
        response = self.client.post(
            url_for('auth.reset_password', token=str(user.id)),
            data=dict(password="newpassword", password2="newpassword"),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Redirects to login
        self.assertIn(b'Your password has been reset.', response.data)
        
        # Verify password change
        self.assertTrue(user.check_password("newpassword"))
        self.assertFalse(user.check_password("password")) # Old password should not work

    def test_access_protected_route_unauthenticated(self):
        response = self.client.get(url_for('main.dashboard'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data) # Should be redirected to login
        self.assertIn(b'Please log in to access this page.', response.data) # Flash message

if __name__ == '__main__':
    unittest.main()
