from app import create_app
from app.analytics.services import prepare_analysis_input
from app.extensions import db
from app.models import Dataset, Institution, StudentRecord, User


def make_app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })
    with app.app_context():
        institution = Institution(name="Analytics Institution")
        db.session.add(institution)
        db.session.flush()
        user = User(
            userid="ANALYTICS",
            email="analytics@example.com",
            institution_id=institution.id,
            first_name="Analytics",
            last_name="Tester",
            role="educator",
            status="active",
            password="hashed",
        )
        dataset = Dataset(
            name="Analytics Dataset",
            source_filename="analytics.csv",
            uploaded_by=user.userid,
            subject="Mathematics",
            grade_scale_max=20,
            g1_label="G1",
            g2_label="G2",
            g3_label="G3",
            import_status="complete",
        )
        db.session.add_all([user, dataset])
        db.session.flush()
        db.session.add_all([
            StudentRecord(student=1, dataset_id=dataset.id, student_name="A", g1=10, g2=12, g3=14, studytime=5, absences=2),
            StudentRecord(student=2, dataset_id=dataset.id, student_name="B", g1=None, g2=14, g3=16, studytime=None, absences=1),
            StudentRecord(student=3, dataset_id=dataset.id, student_name="C", g1=14, g2=None, g3=18, studytime=15, absences=None),
        ])
        db.session.commit()
        return app, dataset.id


def test_preprocessing_calculates_quality_without_excluding_optional_missing_values():
    app, dataset_id = make_app()
    with app.app_context():
        result = prepare_analysis_input(db.session.get(Dataset, dataset_id))

    assert result.quality.total_records == 3
    assert result.quality.valid_g3_records == 3
    assert result.quality.excluded_records == 0
    assert result.quality.missing_g1 == 1
    assert result.quality.missing_g2 == 1
    assert result.quality.missing_studytime == 1
    assert result.quality.missing_absences == 1
    assert list(result.records["g3"]) == [14, 16, 18]


def test_retrieval_is_dataset_scoped():
    app, dataset_id = make_app()
    with app.app_context():
        other = Dataset(
            name="Other", source_filename="other.csv", uploaded_by="ANALYTICS",
            subject="Science", grade_scale_max=20, g3_label="G3",
            import_status="complete",
        )
        db.session.add(other)
        db.session.flush()
        db.session.add(StudentRecord(student=4, dataset_id=other.id, student_name="Other", g3=1))
        db.session.commit()
        result = prepare_analysis_input(db.session.get(Dataset, dataset_id))

    assert list(result.records["student_name"]) == ["A", "B", "C"]
