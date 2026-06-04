from datetime import datetime
from app.models import db

class Student(db.Model):
    __tablename__ = 'tbl_students'

    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.String(20), unique = True, nullable = False)
    full_name = db.Column(db.String(100), nullable = False)
    class_name = db.Column(db.String(50))
    face_saved = db.Column(db.Boolean, default = False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    attendances = db.relationship('Attendance', backref='student',
                                  lazy=True, cascade='all, delete-orphan')