from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256)) # Increased length for potentially longer hashes

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Transcription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', backref=db.backref('transcriptions', lazy=True))

    def __repr__(self):
        return f'<Transcription {self.id} by User {self.user_id} at {self.timestamp}>'

class MoM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    summary = db.Column(db.Text, nullable=False) # The actual MoM content
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    transcription_id = db.Column(db.Integer, db.ForeignKey('transcription.id'), nullable=False, unique=True) # Each transcription can only have one MoM
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # The user who created/owns this MoM

    transcription = db.relationship('Transcription', backref=db.backref('mom', uselist=False, lazy=True)) # one-to-one with Transcription
    user = db.relationship('User', backref=db.backref('moms', lazy=True))

    def __repr__(self):
        return f'<MoM {self.id} for Transcription {self.transcription_id} by User {self.user_id}>'
