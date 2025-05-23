from tests.base_test import BaseTestCase, db
from app.models import User, Transcription, MoM
from app.utils import generate_basic_summary
from flask import url_for

class TestMoMRoutes(BaseTestCase):

    def setUp(self):
        super().setUp()
        # Create a user and a transcription for that user to be used in MoM tests
        self.user = User.query.filter_by(username="testuser").first()
        self.transcription = Transcription(body="This is a detailed test transcription for MoM generation. It has multiple sentences. Hopefully, this is enough content for summarization.", user_id=self.user.id)
        db.session.add(self.transcription)
        db.session.commit()
        self.login() # Log in as the test user

    def tearDown(self):
        self.logout()
        super().tearDown()

    def test_generate_basic_summary_util(self):
        text1 = "First sentence. Second sentence. Third sentence. Fourth sentence."
        summary1 = generate_basic_summary(text1, num_sentences=2, max_chars=100)
        self.assertEqual(summary1, "First sentence. Second sentence.")

        text2 = "This is a very long single sentence that will definitely exceed the character limit of fifty for testing purposes."
        summary2 = generate_basic_summary(text2, num_sentences=1, max_chars=50)
        self.assertEqual(summary2, "This is a very long single sentence that will ...") # Truncated

        text3 = "Short. Even shorter."
        summary3 = generate_basic_summary(text3, num_sentences=3, max_chars=100)
        self.assertEqual(summary3, "Short. Even shorter.")
        
        text4 = ""
        summary4 = generate_basic_summary(text4)
        self.assertEqual(summary4, "")

        text5 = "One sentence only."
        summary5 = generate_basic_summary(text5, num_sentences=3, max_chars=5)
        self.assertEqual(summary5, "One ...")


    def test_manage_mom_page_loads_for_new_mom(self):
        response = self.client.get(url_for('main.manage_mom', transcription_id=self.transcription.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Generate Minutes of Meeting', response.data)
        self.assertIn(b'Original Transcription:', response.data)
        self.assertIn(bytes(self.transcription.body, 'utf-8'), response.data)
        
        # Check if basic summary is pre-filled
        expected_summary = generate_basic_summary(self.transcription.body)
        self.assertIn(bytes(expected_summary, 'utf-8'), response.data)

    def test_create_new_mom(self):
        mom_summary_text = "This is the official MoM summary created by the test."
        response = self.client.post(
            url_for('main.manage_mom', transcription_id=self.transcription.id),
            data={'summary': mom_summary_text},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Redirects to dashboard
        self.assertIn(b'Minutes of Meeting created successfully!', response.data)
        
        mom = MoM.query.filter_by(transcription_id=self.transcription.id).first()
        self.assertIsNotNone(mom)
        self.assertEqual(mom.summary, mom_summary_text)
        self.assertEqual(mom.user_id, self.user.id)
        self.assertEqual(mom.transcription.id, self.transcription.id)

    def test_manage_mom_page_loads_for_existing_mom(self):
        existing_mom_summary = "This MoM already exists."
        mom = MoM(summary=existing_mom_summary, transcription_id=self.transcription.id, user_id=self.user.id)
        db.session.add(mom)
        db.session.commit()

        response = self.client.get(url_for('main.manage_mom', transcription_id=self.transcription.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Minutes of Meeting', response.data)
        self.assertIn(bytes(existing_mom_summary, 'utf-8'), response.data) # Existing summary should be in the form

    def test_update_existing_mom(self):
        initial_summary = "Initial MoM summary."
        mom = MoM(summary=initial_summary, transcription_id=self.transcription.id, user_id=self.user.id)
        db.session.add(mom)
        db.session.commit()

        updated_summary_text = "This is the updated MoM summary."
        response = self.client.post(
            url_for('main.manage_mom', transcription_id=self.transcription.id),
            data={'summary': updated_summary_text},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Redirects to dashboard
        self.assertIn(b'Minutes of Meeting updated successfully!', response.data)
        
        updated_mom = MoM.query.get(mom.id)
        self.assertEqual(updated_mom.summary, updated_summary_text)

    def test_manage_mom_unauthorized_access(self):
        # Create another user and their transcription
        other_user = self.create_test_user(username="otheruser", email="other@example.com", password="otherpassword")
        other_transcription = Transcription(body="Other user's transcription.", user_id=other_user.id)
        db.session.add(other_transcription)
        db.session.commit()

        # Current user (testuser) tries to access MoM page for other_transcription
        response = self.client.get(url_for('main.manage_mom', transcription_id=other_transcription.id), follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Redirects to dashboard
        self.assertIn(b'You are not authorized to access this transcription or MoM.', response.data)
        self.assertIn(b'My Transcriptions Dashboard', response.data) # Check it's the dashboard

        # Try to POST as well
        response = self.client.post(
            url_for('main.manage_mom', transcription_id=other_transcription.id),
            data={'summary': "Attempting to write MoM for other's transcript"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Redirects to dashboard
        self.assertIn(b'You are not authorized to access this transcription or MoM.', response.data)
        self.assertIsNone(MoM.query.filter_by(transcription_id=other_transcription.id).first()) # No MoM should be created

    def test_manage_mom_for_nonexistent_transcription(self):
        non_existent_transcription_id = 9999
        response = self.client.get(url_for('main.manage_mom', transcription_id=non_existent_transcription_id))
        self.assertEqual(response.status_code, 404) # Should be a 404

    def test_dashboard_shows_mom_status(self):
        # Transcription without MoM
        trans1 = self.transcription # Created in setUp, has no MoM initially
        
        # Transcription with MoM
        trans2_body = "Second transcription for MoM status test."
        trans2 = Transcription(body=trans2_body, user_id=self.user.id)
        db.session.add(trans2)
        db.session.commit()
        mom2 = MoM(summary="MoM for trans2", transcription_id=trans2.id, user_id=self.user.id)
        db.session.add(mom2)
        db.session.commit()

        response = self.client.get(url_for('main.dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check button text for trans1 (no MoM)
        # The URL in the href will be something like /transcription/1/mom
        # We need to find the link associated with trans1.body or its ID.
        self.assertIn(bytes(f'href="/transcription/{trans1.id}/mom"', 'utf-8'), response.data)
        self.assertIn(b'Generate MoM', response.data) # Assuming this text is near the link for trans1

        # Check button text for trans2 (has MoM)
        self.assertIn(bytes(f'href="/transcription/{trans2.id}/mom"', 'utf-8'), response.data)
        # This is trickier because "Generate MoM" might appear for trans1.
        # We need to ensure "View/Edit MoM" is associated with trans2.
        # A more robust way would be to parse HTML, but this is a common approach for quick checks.
        # This check assumes the button for trans2 appears after trans1 in the HTML if sorted by ID or body.
        # A better test would isolate the HTML for each transcription item.
        # For now, we'll check if "View/Edit MoM" is present, which it should be for mom2.
        self.assertIn(b'View/Edit MoM', response.data)


if __name__ == '__main__':
    unittest.main()
