import pandas as pd
import pytest

from app.analytics.services import apply_filters


def records():
    return pd.DataFrame({"g1": [10, 12, None, 16], "g2": [12, 14, 15, None], "g3": [14, 16, 18, 20], "studytime": [1, 2, None, 4], "absences": [2, 0, 8, None]})


def test_filters_use_and_logic_and_missing_values_do_not_match():
    result, state = apply_filters(records(), {"studytime_min": "1", "absence_group": "low"})

    assert list(result["g3"]) == [14]
    assert state["studytime_min"] == 1
    assert state["absence_group"] == ["low"]


def test_studytime_category_filter_excludes_missing_values():
    result, _ = apply_filters(records(), {"studytime": "2"})

    assert list(result["g3"]) == [16]


def test_empty_filter_state_returns_original_frame():
    result, state = apply_filters(records(), {})

    assert len(result) == len(records())
    assert state == {}


def test_invalid_ranges_are_rejected():
    with pytest.raises(ValueError, match="minimum cannot be greater"):
        apply_filters(records(), {"studytime_min": "18", "studytime_max": "10"})

    with pytest.raises(ValueError, match="must be a number"):
        apply_filters(records(), {"studytime_min": "many"})

    with pytest.raises(ValueError, match="Unsupported"):
        apply_filters(records(), {"absence_group": "unknown"})
