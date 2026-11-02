from datetime import datetime, timezone

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Dataset, Institution, StudentRecord, User


def make_app():
    app = create_app({"TESTING": True, "SECRET_KEY": "test", "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "WTF_CSRF_ENABLED": False})
    with app.app_context():
        institution = Institution(name="Institution A")
        other = Institution(name="Institution B")
        db.session.add_all([institution, other])
        db.session.flush()
        db.session.add_all([
            User(userid="DMADMIN", email="admin@example.com", institution_id=institution.id, first_name="Data", last_name="Admin", role="admin", status="active", password=generate_password_hash("secret")),
            User(userid="OTHER", email="other@example.com", institution_id=other.id, first_name="Other", last_name="User", role="educator", status="active", password=generate_password_hash("secret")),
        ])
        db.session.flush()
        for index in range(7):
            db.session.add(Dataset(name=f"Dataset {index}", source_filename=f"data{index}.csv", uploaded_by="DMADMIN", subject="Math", grade_scale_max=20, g3_label="Final", import_status="complete", record_count=index + 1, created_at=datetime(2026, 1, index + 1, tzinfo=timezone.utc)))
        db.session.add(Dataset(name="Hidden Dataset", source_filename="hidden.csv", uploaded_by="OTHER", subject="Science", grade_scale_max=20, g3_label="Final", import_status="complete", record_count=2))
        db.session.commit()
    return app


def login_as(client, userid="DMADMIN"):
    with client.session_transaction() as session:
        session["_user_id"] = userid
        session["_fresh"] = True


def test_management_lists_only_current_institution_datasets():
    app = make_app()
    client = app.test_client()
    login_as(client)
    response = client.get("/datasets")
    assert response.status_code == 200
    assert b"Dataset 0" in response.data
    assert b"Hidden Dataset" not in response.data


def test_administrator_and_educator_can_open_management_and_details():
    app = make_app()
    with app.app_context():
        institution = Institution.query.filter_by(name="Institution A").one()
        educator = User(userid="DMEDUCATOR", email="educator@example.com", institution_id=institution.id, first_name="Data", last_name="Educator", role="educator", status="active", password=generate_password_hash("secret"))
        db.session.add(educator)
        dataset_id = Dataset.query.filter_by(name="Dataset 1").one().id
        db.session.commit()
    for userid in ("DMADMIN", "DMEDUCATOR"):
        client = app.test_client()
        login_as(client, userid)
        assert client.get("/datasets").status_code == 200
        assert client.get(f"/datasets/{dataset_id}").status_code == 200


def test_dashboard_shows_six_recent_datasets_and_view_all_link():
    app = make_app()
    client = app.test_client()
    login_as(client)
    response = client.get("/")
    assert response.status_code == 200
    assert response.data.count(b'<article class="cohort-card">') == 6
    assert b"View all" in response.data
    assert b"Dataset 6" in response.data
    assert b"Dataset 0" not in response.data


def test_management_empty_state_links_to_upload():
    app = make_app()
    with app.app_context():
        Dataset.query.delete()
        db.session.commit()
    client = app.test_client()
    login_as(client)
    response = client.get("/datasets")
    assert b"No datasets imported yet" in response.data
    assert b"/datasets/upload" in response.data
    assert b"Upload your first dataset" in response.data
    assert b"dataset-management-empty" in response.data


def test_detail_displays_stored_metadata_and_authoritative_records():
    app = make_app()
    with app.app_context():
        dataset = Dataset.query.filter_by(name="Dataset 0").one()
        db.session.add(StudentRecord(student=9001, dataset_id=dataset.id, student_name="Student A", g3=18))
        db.session.commit()
        dataset_id = dataset.id
    client = app.test_client()
    login_as(client)
    response = client.get(f"/datasets/{dataset_id}")
    assert response.status_code == 200
    assert b"Student A" in response.data
    assert b"Records" in response.data
    assert b">1<" in response.data
    assert b"Final" in response.data


def test_detail_hides_dataset_from_other_institution():
    app = make_app()
    with app.app_context():
        hidden = Dataset.query.filter_by(name="Hidden Dataset").one()
        hidden_id = hidden.id
    client = app.test_client()
    login_as(client)
    response = client.get(f"/datasets/{hidden_id}")
    assert response.status_code == 404


def test_user_can_select_dataset_and_selection_persists():
    app = make_app()
    with app.app_context():
        dataset_id = Dataset.query.filter_by(name="Dataset 1").one().id
    client = app.test_client()
    login_as(client)
    response = client.post(f"/datasets/{dataset_id}/select", follow_redirects=True)
    assert response.status_code == 200
    assert b"Set for analysis" in response.data
    with client.session_transaction() as session:
        assert session["active_dataset_id"] == dataset_id


def test_selection_rejects_dataset_from_other_institution():
    app = make_app()
    with app.app_context():
        dataset_id = Dataset.query.filter_by(name="Hidden Dataset").one().id
    client = app.test_client()
    login_as(client)
    response = client.post(f"/datasets/{dataset_id}/select")
    assert response.status_code == 404
    with client.session_transaction() as session:
        assert "active_dataset_id" not in session


def test_selection_rejects_malformed_and_nonexistent_ids():
    app = make_app()
    client = app.test_client()
    login_as(client)
    assert client.post("/datasets/not-an-id/select").status_code == 404
    assert client.post("/datasets/999999/select").status_code == 404


def test_dashboard_to_detail_to_selection_workflow():
    app = make_app()
    with app.app_context():
        dataset_id = Dataset.query.filter_by(name="Dataset 1").one().id
    client = app.test_client()
    login_as(client)
    dashboard = client.get("/")
    assert f"/datasets/{dataset_id}".encode() in dashboard.data
    detail = client.get(f"/datasets/{dataset_id}")
    assert b"Set for Analysis" in detail.data
    selected = client.post(f"/datasets/{dataset_id}/select", follow_redirects=True)
    assert b"Set for analysis" in selected.data


def test_invalid_active_selection_is_cleared():
    app = make_app()
    client = app.test_client()
    login_as(client)
    with client.session_transaction() as session:
        session["active_dataset_id"] = "not-an-id"
    response = client.get("/datasets")
    assert response.status_code == 200
    with client.session_transaction() as session:
        assert "active_dataset_id" not in session


def test_detail_shows_stored_import_information_without_inventing_history():
    app = make_app()
    with app.app_context():
        dataset = Dataset.query.filter_by(name="Dataset 0").one()
        dataset.department = None
        dataset.source_filename = "authoritative.csv"
        dataset.import_status = "complete"
        db.session.commit()
        dataset_id = dataset.id
    client = app.test_client()
    login_as(client)
    response = client.get(f"/datasets/{dataset_id}")
    assert b"Import information" in response.data
    assert b"authoritative.csv" in response.data
    assert b"complete" in response.data
    assert b"Not recorded" in response.data
    assert b"No separate import-history records are stored" in response.data
