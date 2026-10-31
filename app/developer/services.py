"""Allowlisted, read-only Developer database resources."""

from dataclasses import dataclass
import re

from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Dataset, Institution, StudentRecord, UploadError, User


@dataclass(frozen=True)
class ResourceDefinition:
    key: str
    label: str
    model: object
    fields: tuple[str, ...]
    redacted_fields: tuple[str, ...] = ()
    editable_fields: tuple[str, ...] = ()


RESOURCE_DEFINITIONS = {
    "users": ResourceDefinition("users", "Users", User, ("userid", "email", "institution_id", "first_name", "last_name", "title", "role", "status", "created_at", "updated_at"), ("password",), ("email", "first_name", "last_name", "title", "status")),
    "institutions": ResourceDefinition("institutions", "Institutions", Institution, ("id", "name", "created_at")),
    "datasets": ResourceDefinition("datasets", "Datasets", Dataset, ("id", "name", "source_filename", "uploaded_by", "subject", "department", "academic_year", "class_section", "grade_scale_max", "g1_label", "g2_label", "g3_label", "import_status", "record_count", "created_at"), (), ("name", "subject", "department", "academic_year", "class_section", "grade_scale_max", "g1_label", "g2_label", "g3_label")),
    "student_records": ResourceDefinition("student_records", "Student Records", StudentRecord, ("student", "dataset_id", "student_name", "g1", "g2", "g3", "studytime", "absences"), (), ("student_name", "g1", "g2", "g3", "studytime", "absences")),
    "upload_errors": ResourceDefinition("upload_errors", "Upload Errors", UploadError, ("id", "dataset_id", "row_number", "column_name", "error_message", "created_at")),
}


def get_resource(resource_key):
    return RESOURCE_DEFINITIONS.get(resource_key)


def serialize_record(record, definition):
    return {field: getattr(record, field) for field in definition.fields if field not in definition.redacted_fields}


def _validate_value(record, field, value):
    if field in {"first_name", "last_name", "title", "name", "subject", "department", "academic_year", "class_section", "g1_label", "g2_label", "g3_label", "student_name"}:
        if len(value) > 150:
            raise ValueError(f"{field} is too long.")
        if field in {"first_name", "last_name", "name", "subject", "student_name"} and not value:
            raise ValueError(f"{field} is required.")
        return value or None
    if field == "email":
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Enter a valid email address.")
        return value.lower()
    if field == "status":
        if value not in {"active", "inactive"}:
            raise ValueError("Invalid account status.")
        return value
    if field == "grade_scale_max":
        parsed = int(value)
        if parsed <= 0:
            raise ValueError("Grade scale must be positive.")
        return parsed
    if field in {"g1", "g2", "g3", "studytime"}:
        return None if value == "" else float(value)
    if field == "absences":
        parsed = int(value)
        if parsed < 0:
            raise ValueError("Absences cannot be negative.")
        return parsed
    raise ValueError(f"Field {field} is not editable.")


def update_record(definition, record, submitted):
    unknown = set(submitted) - set(definition.editable_fields)
    if unknown:
        raise ValueError("One or more submitted fields are not editable.")
    for field, value in submitted.items():
        setattr(record, field, _validate_value(record, field, str(value).strip()))
    if isinstance(record, StudentRecord):
        if record.g3 is None:
            raise ValueError("Final grade is required.")
        dataset = db.session.get(Dataset, record.dataset_id)
        if dataset is None:
            raise ValueError("Student record dataset does not exist.")
        for grade in (record.g1, record.g2, record.g3):
            if grade is not None and not 0 <= grade <= dataset.grade_scale_max:
                raise ValueError("Grade is outside the parent dataset scale.")
    try:
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()
        raise ValueError("The update could not be saved.") from error
    return record
