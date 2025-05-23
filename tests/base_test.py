import unittest
from app import create_app, db
from app.config import TestConfig
from app.models import User, Transcription, MoM

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # You can also create some common test users or data here if needed by many tests
        self.create_test_user()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_test_user(self, username="testuser", email="test@example.com", password="password"):
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def login(self, username="testuser", password="password"):
        return self.client.post(
            '/auth/login',
            data=dict(username=username, password=password),
            follow_redirects=True
        )

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)

if __name__ == '__main__':
    unittest.main()
