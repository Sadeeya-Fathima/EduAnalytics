from tests.test_analytics_preprocessing import make_app
from app.analytics.services import apply_filters, prepare_analysis_input
from app.extensions import db
from app.models import Dataset, StudentRecord


def login_as(client):
    with client.session_transaction() as session:
        session["_user_id"] = "ANALYTICS"
        session["_fresh"] = True


def test_authorized_user_can_open_dataset_analytics():
    app, dataset_id = make_app()
    client = app.test_client()
    login_as(client)

    response = client.get(f"/analytics/{dataset_id}")

    assert response.status_code == 200
    assert b"Class Performance Overview" in response.data
    assert b"Overall class performance" in response.data
    assert b"Detailed Statistics" in response.data
    assert b"grade distribution" in response.data
    assert b"Assessment comparison" in response.data
    assert b"analyticsData" in response.data


def test_analytics_requires_login():
    app, dataset_id = make_app()

    response = app.test_client().get(f"/analytics/{dataset_id}")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_dashboard_filters_update_matching_count_and_can_reset():
    app, dataset_id = make_app()
    client = app.test_client()
    login_as(client)

    filtered = client.get(f"/analytics/{dataset_id}?studytime_min=5&absence_group=low")
    assert filtered.status_code == 200
    assert b"1 matching records" in filtered.data
    assert b"Total students" in filtered.data

    reset = client.get(f"/analytics/{dataset_id}")
    assert reset.status_code == 200
    assert b"3 matching records" in reset.data


def test_dashboard_rejects_invalid_filter():
    app, dataset_id = make_app()
    client = app.test_client()
    login_as(client)

    response = client.get(f"/analytics/{dataset_id}?studytime_min=18&studytime_max=10")

    assert response.status_code == 400


def test_dashboard_marks_unavailable_studytime_and_absences():
    app, dataset_id = make_app()
    with app.app_context():
        records = StudentRecord.query.filter_by(dataset_id=dataset_id).all()
        for record in records:
            record.studytime = None
            record.absences = None
        db.session.commit()

    client = app.test_client()
    login_as(client)
    response = client.get(f"/analytics/{dataset_id}")

    assert response.status_code == 200
    assert b"Study-time analysis is unavailable for this dataset." in response.data
    assert b"Attendance analysis is unavailable for this dataset." in response.data


def test_dataset_quality_remains_unfiltered_when_filters_are_applied():
    app, dataset_id = make_app()
    with app.app_context():
        dataset = db.session.get(Dataset, dataset_id)
        original = prepare_analysis_input(dataset).quality
        filtered, _ = apply_filters(prepare_analysis_input(dataset).records, {"g3_min": "16"}, dataset.grade_scale_max)

    assert original.total_records == 3
    assert original.valid_g3_records == 3
    assert len(filtered) == 2
