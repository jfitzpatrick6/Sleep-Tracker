from . import db
from flask_login import UserMixin
from datetime import date

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

class SleepEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sleep_date = db.Column(db.Date, nullable=False)
    hours_slept = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Make date unique per user
    __table_args__ = (db.UniqueConstraint('user_id', 'sleep_date', name='uq_user_sleep_date'),)

    def __repr__(self):
        return f"<Sleep {self.sleep_date} - {self.hours_slept}h>"