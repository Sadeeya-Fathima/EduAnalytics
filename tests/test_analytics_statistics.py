import pandas as pd

from app.analytics.services import calculate_grade_distribution, calculate_grade_statistics


def test_grade_statistics_use_population_stddev_and_linear_quartiles():
    records = pd.DataFrame({"g3": [14, 16, 18, 12]})

    result = calculate_grade_statistics(records)

    assert result.count == 4
    assert result.mean == 15
    assert result.median == 15
    assert result.minimum == 12
    assert result.maximum == 18
    assert abs(result.population_stddev - 2.2360679) < 1e-6
    assert result.q1 == 13.5
    assert result.q3 == 16.5


def test_grade_distribution_has_non_overlapping_decimal_boundaries():
    records = pd.DataFrame({"g3": [0, 4.99, 5, 8.99, 9, 12.99, 13, 16.99, 17, 20]})

    result = calculate_grade_distribution(records, 20)

    assert [band.count for band in result] == [2, 2, 2, 2, 2]
    assert sum(band.count for band in result) == 10
    assert sum(band.percentage for band in result) == 100


def test_empty_statistics_are_unavailable_and_distribution_is_zeroed():
    records = pd.DataFrame({"g3": [None, "invalid"]})

    statistics = calculate_grade_statistics(records)
    distribution = calculate_grade_distribution(records, 20)

    assert statistics.count == 0
    assert statistics.mean is None
    assert statistics.population_stddev is None
    assert all(band.count == 0 and band.percentage == 0 for band in distribution)
