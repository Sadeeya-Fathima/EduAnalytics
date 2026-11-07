import pandas as pd

from app.analytics.services import assessment_scatter_data


def test_assessment_scatter_uses_only_paired_values_and_no_identity_fields():
    records = pd.DataFrame({"student_name": ["A", "B", "C"], "g1": [10, None, 14], "g3": [14, 16, 18]})

    result = assessment_scatter_data(records, "g1")

    assert result == [{"assessment": 10.0, "g3": 14.0}, {"assessment": 14.0, "g3": 18.0}]
    assert all("student_name" not in point for point in result)


def test_assessment_scatter_is_empty_when_field_is_unavailable():
    records = pd.DataFrame({"g3": [14, 16]})

    assert assessment_scatter_data(records, "g1") == []
