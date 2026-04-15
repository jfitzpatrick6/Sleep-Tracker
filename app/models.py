from . import db
from datetime import date

class SleepEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sleep_date = db.Column(db.Date, unique=True, nullable=False)
    hours_slept = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Sleep {self.sleep_date} - {self.hours_slept}h>"