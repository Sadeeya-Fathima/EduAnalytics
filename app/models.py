
from flask_login import UserMixin
from datetime import datetime, timezone

from app.extensions import db


def utc_now():
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


class Institution(db.Model):
    __tablename__ = "institution"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=utc_now, nullable=False
    )

    users = db.relationship("User", back_populates="institution")


class User(UserMixin, db.Model):
    __tablename__ = "users"

    userid = db.Column(db.String(80), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    institution_id = db.Column(
        db.Integer, db.ForeignKey("institution.id"), nullable=False
    )
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="active", nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    password = db.Column(db.String(255), nullable=False)

    institution = db.relationship("Institution", back_populates="users")
    datasets = db.relationship("Dataset", back_populates="uploader")

    def get_id(self):
        """Return the string userid used by Flask-Login."""
        return str(self.userid)

class Dataset(db.Model):
    __tablename__ = "datasets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    source_filename = db.Column(db.String(255), nullable=False)
    uploaded_by = db.Column(
        db.String(80), db.ForeignKey("users.userid"), nullable=False
    )
    subject = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    academic_year = db.Column(db.String(20), nullable=True)
    class_section = db.Column(db.String(100), nullable=True)
    grade_scale_max = db.Column(db.Integer, nullable=False)
    g1_label = db.Column(db.String(100), nullable=True)
    g2_label = db.Column(db.String(100), nullable=True)
    g3_label = db.Column(
        db.String(100), default="Final Grade", nullable=False
    )
    import_status = db.Column(
        db.String(20), default="pending", nullable=False
    )
    record_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=utc_now, nullable=False
    )

    uploader = db.relationship("User", back_populates="datasets")
    student_records = db.relationship(
        "StudentRecord", back_populates="dataset"
    )
    upload_errors = db.relationship(
        "UploadError", back_populates="dataset"
    )

class StudentRecord(db.Model):
    __tablename__ = "student_records"

    student = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(
        db.Integer, db.ForeignKey("datasets.id"), nullable=False
    )
    student_name = db.Column(db.String(150), nullable=False)
    g1 = db.Column(db.Float, nullable=True)
    g2 = db.Column(db.Float, nullable=True)
    g3 = db.Column(db.Float, nullable=False)
    studytime = db.Column(db.Float, nullable=True)
    absences = db.Column(db.Integer, nullable=True)

    dataset = db.relationship("Dataset", back_populates="student_records")

class UploadError(db.Model):
    __tablename__ = "upload_errors"

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(
        db.Integer, db.ForeignKey("datasets.id"), nullable=True
    )
    row_number = db.Column(db.Integer, nullable=True)
    column_name = db.Column(db.String(100), nullable=True)
    error_message = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=utc_now, nullable=False
    )

    dataset = db.relationship("Dataset", back_populates="upload_errors")
