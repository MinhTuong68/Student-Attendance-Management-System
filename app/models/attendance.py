from datetime import datetime
from app.models import db

class Attendance(db.Model):
    __tablename__ = 'tbl_attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('tbl_students.id'), nullable=False)
    timestamp  = db.Column(db.DateTime, default=datetime.utcnow)
    similarity = db.Column(db.Float)
    method     = db.Column(db.String(10), default='auto')

    