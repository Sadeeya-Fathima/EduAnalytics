from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import AuditEvent, Dataset, Institution, StudentRecord, User


def crud_app():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret-key", "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "WTF_CSRF_ENABLED": False, "EDUANALYTICS_ENV": "development", "EDUANALYTICS_DEV_TOOLS_ENABLED": True})
    with app.app_context():
        institution = Institution(name="Test Institution")
        db.session.add(institution)
        db.session.flush()
        db.session.add(User(userid="DEV001", email="dev@example.com", institution_id=institution.id, first_name="Dev", last_name="User", role="developer", status="active", password=generate_password_hash("secret")))
        dataset = Dataset(name="Math", source_filename="math.csv", uploaded_by="DEV001", subject="Math", grade_scale_max=20, import_status="complete")
        db.session.add(dataset)
        db.session.flush()
        db.session.add(StudentRecord(student=1, dataset_id=dataset.id, student_name="Student One", g3=15, g1=12, g2=14))
        db.session.commit()
    return app


def login(client):
    with client.session_transaction() as session:
        session["_user_id"] = "DEV001"
        session["_fresh"] = True


def test_user_update_is_allowlisted_and_audited():
    app = crud_app()
    client = app.test_client()
    login(client)
    response = client.post("/developer/database/records/users/DEV001/edit", data={"first_name": "Updated", "last_name": "User", "email": "updated@example.com", "title": "Maintainer", "status": "active"}, environ_base={"REMOTE_ADDR": "127.0.0.1"})
    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(User, "DEV001").first_name == "Updated"
        assert AuditEvent.query.filter_by(action="record_update", outcome="success").count() == 1


def test_user_role_change_is_rejected():
    app = crud_app()
    client = app.test_client()
    login(client)
    response = client.post("/developer/database/records/users/DEV001/edit", data={"role": "admin"}, environ_base={"REMOTE_ADDR": "127.0.0.1"})
    assert response.status_code == 400
    with app.app_context():
        assert db.session.get(User, "DEV001").role == "developer"


def test_student_record_cannot_change_parent_dataset():
    app = crud_app()
    client = app.test_client()
    login(client)
    response = client.post("/developer/database/records/student_records/1/edit", data={"dataset_id": "999"}, environ_base={"REMOTE_ADDR": "127.0.0.1"})
    assert response.status_code == 400
    with app.app_context():
        assert db.session.get(StudentRecord, 1).dataset_id == 1
        assert AuditEvent.query.filter_by(action="record_update", outcome="failure").count() == 1


def test_student_record_grade_must_respect_dataset_scale():
    app = crud_app()
    client = app.test_client()
    login(client)
    response = client.post("/developer/database/records/student_records/1/edit", data={"student_name": "Student One", "g1": "99", "g2": "14", "g3": "15", "studytime": "", "absences": "0"}, environ_base={"REMOTE_ADDR": "127.0.0.1"})
    assert response.status_code == 400
    with app.app_context():
        assert db.session.get(StudentRecord, 1).g1 == 12
