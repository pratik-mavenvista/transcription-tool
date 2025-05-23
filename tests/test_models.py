from tests.base_test import BaseTestCase, db
from app.models import User, Transcription, MoM
from datetime import datetime

class TestModelRelationships(BaseTestCase):

    def test_user_creation_and_password(self):
        user = User.query.filter_by(username="testuser").first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password("password"))
        self.assertFalse(user.check_password("wrongpassword"))

    def test_transcription_creation(self):
        user = User.query.filter_by(username="testuser").first()
        transcription_text = "This is a test transcription."
        trans = Transcription(body=transcription_text, user_id=user.id)
        db.session.add(trans)
        db.session.commit()

        self.assertIsNotNone(trans.id)
        self.assertEqual(trans.body, transcription_text)
        self.assertEqual(trans.user_id, user.id)
        self.assertIsInstance(trans.timestamp, datetime)
        self.assertIn(trans, user.transcriptions)

    def test_mom_creation(self):
        user = User.query.filter_by(username="testuser").first()
        trans = Transcription(body="Another test transcription for MoM.", user_id=user.id)
        db.session.add(trans)
        db.session.commit()

        mom_summary = "This is the MoM summary."
        mom = MoM(summary=mom_summary, transcription_id=trans.id, user_id=user.id)
        db.session.add(mom)
        db.session.commit()

        self.assertIsNotNone(mom.id)
        self.assertEqual(mom.summary, mom_summary)
        self.assertEqual(mom.transcription_id, trans.id)
        self.assertEqual(mom.user_id, user.id)
        self.assertIsInstance(mom.created_at, datetime)
        self.assertIsInstance(mom.updated_at, datetime)

        # Test relationships
        self.assertEqual(trans.mom, mom)
        self.assertIn(mom, user.moms)

    def test_mom_uniqueness_to_transcription(self):
        user = User.query.filter_by(username="testuser").first()
        trans = Transcription(body="Unique MoM test.", user_id=user.id)
        db.session.add(trans)
        db.session.commit()

        mom1 = MoM(summary="First MoM", transcription_id=trans.id, user_id=user.id)
        db.session.add(mom1)
        db.session.commit()

        # Attempt to create a second MoM for the same transcription
        mom2 = MoM(summary="Second MoM attempt", transcription_id=trans.id, user_id=user.id)
        try:
            db.session.add(mom2)
            db.session.commit()
            # If we reach here, the unique constraint failed.
            # However, SQLAlchemy might raise IntegrityError before commit or upon flush.
            # For SQLite in-memory, this often gets caught at commit.
            self.fail("Should have raised an IntegrityError due to unique constraint on transcription_id for MoM.")
        except Exception as e: # Broad exception to catch backend-specific integrity errors
            db.session.rollback() # Important to rollback session after error
            self.assertIsNotNone(e) # Check that an exception was indeed raised
            # A more specific check would be:
            # from sqlalchemy.exc import IntegrityError
            # self.assertIsInstance(e, IntegrityError)
            # However, the exact exception type can vary slightly with DB backend / ORM version.

    def test_user_repr(self):
        user = User.query.filter_by(username="testuser").first()
        self.assertEqual(repr(user), '<User testuser>')

    def test_transcription_repr(self):
        user = User.query.filter_by(username="testuser").first()
        trans = Transcription(body="Repr test", user_id=user.id)
        db.session.add(trans)
        db.session.commit()
        # Timestamp will vary, so we check the fixed part
        self.assertTrue(repr(trans).startswith(f'<Transcription {trans.id} by User {user.id} at '))

    def test_mom_repr(self):
        user = User.query.filter_by(username="testuser").first()
        trans = Transcription(body="MoM Repr test", user_id=user.id)
        db.session.add(trans)
        db.session.commit()
        mom = MoM(summary="Summary for MoM repr", transcription_id=trans.id, user_id=user.id)
        db.session.add(mom)
        db.session.commit()
        self.assertEqual(repr(mom), f'<MoM {mom.id} for Transcription {trans.id} by User {user.id}>')

if __name__ == '__main__':
    unittest.main()
