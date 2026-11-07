import pandas as pd

from app.analytics.services import (
    calculate_absence_analysis,
    calculate_assessment_summaries,
    calculate_correlation,
    calculate_studytime_analysis,
)


def test_assessments_use_available_values_and_paired_differences():
    records = pd.DataFrame({"g1": [10, None, 14], "g2": [12, 14, None], "g3": [14, 16, 18]})

    result = calculate_assessment_summaries(records)

    assert [(item.field, item.count) for item in result] == [("g1", 2), ("g2", 2), ("g3", 3)]
    assert result[0].paired_count_with_g3 == 2
    assert result[0].mean_paired_difference_from_g3 == 4


def test_categorical_studytime_does_not_produce_hour_average_or_correlation():
    records = pd.DataFrame({"studytime": [1, 1, 2], "g3": [10, 12, 16]})

    result = calculate_studytime_analysis(records, categorical=True)

    assert result["available"] is True
    assert result["average"] is None
    assert [group.count for group in result["groups"]] == [2, 1]


def test_absence_groups_and_correlation_safeguards():
    records = pd.DataFrame({"absences": [0, 1, 6, 11], "g3": [10, 12, 14, 16]})

    groups = calculate_absence_analysis(records)
    correlation = calculate_correlation(records, "absences")
    constant = calculate_correlation(pd.DataFrame({"absences": [1, 1, 1], "g3": [10, 12, 14]}), "absences")

    assert [group.count for group in groups["groups"]] == [1, 1, 1, 1]
    assert correlation.paired_count == 4
    assert correlation.coefficient is not None
    assert correlation.interpretation_eligible is False
    assert constant.coefficient is None
