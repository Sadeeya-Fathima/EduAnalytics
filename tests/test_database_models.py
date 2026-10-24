
import pytest
from sqlalchemy.exc import IntegrityError

from app import create_app
from app.extensions import db
from app.models import Institution, User, Dataset, StudentRecord, UploadError


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def session(app):
    with app.app_context():
        yield db.session
        db.session.rollback()
        db.session.remove()


def make_institution(session):
    institution = Institution(name="Test Institution")
    session.add(institution)
    session.flush()
    return institution



def make_user(
    session,
    institution,
    userid="TEST001",
    email="teacher@example.com",
    role="educator",
    title=None,
):
    user = User(
        userid=userid,
        email=email,
        institution_id=institution.id,
        first_name="Test",
        last_name="User",
        title=title,
        role=role,
        status="active",
        password="test-hash",
    )
    session.add(user)
    session.flush()
    return user


def test_create_and_read_institution_and_user(session):
    institution = make_institution(session)
    user = make_user(session, institution)
    session.commit()

    saved_user = session.get(User, "TEST001")

    assert saved_user is not None
    assert saved_user.email == "teacher@example.com"
    assert saved_user.institution.name == "Test Institution"
    assert institution.users[0].userid == "TEST001"


def test_user_can_have_no_title(session):
    institution = make_institution(session)
    user = make_user(session, institution, title=None)
    session.commit()

    assert session.get(User, user.userid).title is None



def test_duplicate_email_is_rejected(session):
    institution = make_institution(session)

    make_user(
        session,
        institution,
        userid="TEST001",
        email="same@example.com",
    )
    session.commit()

    with pytest.raises(IntegrityError):
        make_user(
            session,
            institution,
            userid="TEST002",
            email="same@example.com",
        )

    session.rollback()

def test_invalid_institution_foreign_key_is_rejected(session):
    user = User(
        userid="TEST003",
        email="invalid@example.com",
        institution_id=99999,
        first_name="Invalid",
        last_name="Institution",
        role="educator",
        status="active",
        password="test-hash",
    )
    session.add(user)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


def test_dataset_student_record_and_upload_error_relationships(session):
    institution = make_institution(session)
    user = make_user(session, institution)

    dataset = Dataset(
        name="Test Mathematics",
        source_filename="sample.csv",
        uploaded_by=user.userid,
        subject="Mathematics",
        grade_scale_max=20,
        g1_label="First Internal",
        g2_label="Second Internal",
        g3_label="Final Exam",
    )
    session.add(dataset)
    session.flush()

    record = StudentRecord(
        dataset_id=dataset.id,
        student_name="Student 001",
        g1=12,
        g2=14,
        g3=16,
        studytime=None,
        absences=None,
    )
    error = UploadError(
        dataset_id=dataset.id,
        row_number=3,
        column_name="g3",
        error_message="Example validation error",
    )

    session.add_all([record, error])
    session.commit()

    saved_dataset = session.get(Dataset, dataset.id)

    assert saved_dataset.uploader.userid == user.userid
    assert saved_dataset.student_records[0].student_name == "Student 001"
    assert saved_dataset.upload_errors[0].column_name == "g3"
    assert saved_dataset.student_records[0].studytime is None
    assert saved_dataset.student_records[0].absences is None


def test_upload_error_can_exist_without_dataset(session):
    error = UploadError(
        dataset_id=None,
        row_number=2,
        column_name="g3",
        error_message="Required value is missing",
    )
    session.add(error)
    session.commit()

    saved_error = session.get(UploadError, error.id)

    assert saved_error.dataset_id is None
    assert saved_error.dataset is None


def test_institution_name_is_required(session):
    institution = Institution(name=None)
    session.add(institution)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()
