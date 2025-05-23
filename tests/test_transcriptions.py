from tests.base_test import BaseTestCase, db
from app.models import User, Transcription
from flask import url_for

class TestTranscriptionRoutes(BaseTestCase):

    def test_transcribe_page_loads_for_logged_in_user(self):
        self.login()
        response = self.client.get(url_for('main.transcribe'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Live Transcription', response.data)
        self.logout()

    def test_transcribe_page_redirects_for_anonymous_user(self):
        response = self.client.get(url_for('main.transcribe'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data) # Redirected to login
        self.assertIn(b'Please log in to access this page.', response.data)

    def test_save_transcription_success(self):
        self.login()
        user = User.query.filter_by(username="testuser").first()
        transcript_text = "This is a saved transcript."
        
        response = self.client.post(
            url_for('main.save_transcription'),
            json={'transcription': transcript_text}
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'success')
        self.assertEqual(json_data['message'], 'Transcription saved')

        saved_transcription = Transcription.query.filter_by(user_id=user.id).first()
        self.assertIsNotNone(saved_transcription)
        self.assertEqual(saved_transcription.body, transcript_text)
        self.logout()

    def test_save_transcription_empty_text(self):
        self.login()
        response = self.client.post(
            url_for('main.save_transcription'),
            json={'transcription': '   '} # Empty or whitespace only
        )
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'error')
        self.assertEqual(json_data['message'], 'Transcription is empty')
        self.logout()

    def test_save_transcription_no_data(self):
        self.login()
        response = self.client.post(
            url_for('main.save_transcription'),
            json={} # No transcription key
        )
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'error')
        self.assertEqual(json_data['message'], 'No transcription data provided')
        self.logout()

    def test_save_transcription_unauthenticated(self):
        response = self.client.post(
            url_for('main.save_transcription'),
            json={'transcription': 'Trying to save this'},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Redirects to login
        self.assertIn(b'Sign In', response.data)
        self.assertIn(b'Please log in to access this page.', response.data)
        self.assertEqual(Transcription.query.count(), 0) # No transcription should be saved

    def test_dashboard_loads_for_logged_in_user(self):
        self.login()
        user = User.query.filter_by(username="testuser").first()
        # Create some transcriptions for this user
        db.session.add(Transcription(body="First transcript", user_id=user.id))
        db.session.add(Transcription(body="Second transcript", user_id=user.id))
        db.session.commit()

        response = self.client.get(url_for('main.dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'My Transcriptions Dashboard', response.data)
        self.assertIn(b'First transcript', response.data)
        self.assertIn(b'Second transcript', response.data)
        self.logout()
        
    def test_dashboard_shows_only_user_transcriptions(self):
        user1 = self.create_test_user(username="user1", email="user1@example.com", password="pw1")
        user2 = self.create_test_user(username="user2", email="user2@example.com", password="pw2")

        db.session.add(Transcription(body="User1 transcript", user_id=user1.id))
        db.session.add(Transcription(body="User2 transcript", user_id=user2.id))
        db.session.commit()

        self.login(username="user1", password="pw1")
        response = self.client.get(url_for('main.dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User1 transcript', response.data)
        self.assertNotIn(b'User2 transcript', response.data)
        self.logout()

        self.login(username="user2", password="pw2")
        response = self.client.get(url_for('main.dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'User1 transcript', response.data)
        self.assertIn(b'User2 transcript', response.data)
        self.logout()


    def test_dashboard_pagination(self):
        self.login()
        user = User.query.filter_by(username="testuser").first()
        for i in range(7): # Create 7 transcriptions
            db.session.add(Transcription(body=f"Transcript {i+1}", user_id=user.id))
        db.session.commit()

        # Test first page
        response = self.client.get(url_for('main.dashboard', page=1))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Transcript 7', response.data) # Newest first
        self.assertIn(b'Transcript 6', response.data)
        self.assertIn(b'Transcript 5', response.data)
        self.assertIn(b'Transcript 4', response.data)
        self.assertIn(b'Transcript 3', response.data)
        self.assertNotIn(b'Transcript 2', response.data) # Assuming per_page=5
        self.assertIn(b'Next', response.data)
        self.assertNotIn(b'Previous', response.data) # On first page

        # Test second page
        response = self.client.get(url_for('main.dashboard', page=2))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Transcript 7', response.data)
        self.assertIn(b'Transcript 2', response.data)
        self.assertIn(b'Transcript 1', response.data)
        self.assertNotIn(b'Next', response.data) # On last page
        self.assertIn(b'Previous', response.data)
        self.logout()

    def test_dashboard_empty_state(self):
        self.login() # testuser has no transcriptions initially in this specific test
        # Ensure no transcriptions exist for testuser if setUp creates them by default
        # For this test, let's use a new user or ensure testuser has no transcriptions
        current_user = User.query.filter_by(username="testuser").first()
        Transcription.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        response = self.client.get(url_for('main.dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"You don't have any saved transcriptions yet.", response.data)
        self.logout()

if __name__ == '__main__':
    unittest.main()
