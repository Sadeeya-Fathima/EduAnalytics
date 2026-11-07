"""Request-scoped dataset retrieval and preprocessing for Sprint 7."""

from dataclasses import dataclass

import pandas as pd

from app.models import Dataset, StudentRecord


ANALYSIS_COLUMNS = (
    "student",
    "student_name",
    "g1",
    "g2",
    "g3",
    "studytime",
    "absences",
)


@dataclass(frozen=True)
class DatasetQuality:
    """Quality measurements calculated from the complete selected dataset."""

    total_records: int
    valid_g3_records: int
    excluded_records: int
    missing_g1: int | None
    missing_g2: int | None
    missing_studytime: int
    missing_absences: int


@dataclass(frozen=True)
class AnalysisInput:
    """Temporary, request-scoped input prepared for later analytics phases."""

    dataset: Dataset
    records: pd.DataFrame
    quality: DatasetQuality


@dataclass(frozen=True)
class GradeStatistics:
    """Descriptive statistics for valid final-grade observations."""

    count: int
    mean: float | None
    median: float | None
    minimum: float | None
    maximum: float | None
    population_stddev: float | None
    q1: float | None
    q3: float | None


@dataclass(frozen=True)
class GradeBand:
    """One non-overlapping final-grade distribution band."""

    label: str
    lower: float
    upper: float
    include_upper: bool
    count: int
    percentage: float


@dataclass(frozen=True)
class AssessmentSummary:
    """Summary and paired comparison values for one assessment column."""

    field: str
    count: int
    mean: float | None
    paired_count_with_g3: int
    mean_paired_difference_from_g3: float | None


@dataclass(frozen=True)
class AnalysisGroup:
    """One group in a study-time or absence comparison."""

    label: str
    count: int
    average_g3: float | None


@dataclass(frozen=True)
class CorrelationResult:
    """Safely calculated Pearson correlation metadata."""

    x_field: str
    y_field: str
    paired_count: int
    coefficient: float | None
    interpretation_eligible: bool


@dataclass(frozen=True)
class StatisticalFinding:
    """Deterministic, non-causal dashboard observation."""

    category: str
    text: str


def apply_filters(records: pd.DataFrame, params, grade_scale_max: float = 20) -> tuple[pd.DataFrame, dict]:
    """Apply validated AND filters and return filtered records plus state."""
    filtered = records.copy()
    state = {}

    def values_for(name):
        if hasattr(params, "getlist"):
            return [value.strip() for value in params.getlist(name) if value.strip()]
        value = params.get(name, "")
        return [value.strip()] if value and value.strip() else []

    def number_value(name):
        values = values_for(name)
        if not values:
            return None
        if len(values) != 1:
            raise ValueError(f"{name} must contain one number.")
        try:
            value = float(values[0])
        except ValueError as error:
            raise ValueError(f"{name} must be a number.") from error
        if value < 0 or value > grade_scale_max:
            raise ValueError(f"{name} must be between 0 and {grade_scale_max}.")
        return value

    for field in ("g1", "g2", "g3"):
        minimum = number_value(f"{field}_min")
        maximum = number_value(f"{field}_max")
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError(f"{field} minimum cannot be greater than maximum.")
        if minimum is not None or maximum is not None:
            values = pd.to_numeric(filtered[field], errors="coerce")
            if minimum is not None:
                filtered = filtered[values >= minimum]
            if maximum is not None:
                filtered = filtered[values <= maximum]
            state[f"{field}_min"] = minimum
            state[f"{field}_max"] = maximum

    study_min = number_value("studytime_min")
    study_max = number_value("studytime_max")
    if study_min is not None and study_max is not None and study_min > study_max:
        raise ValueError("studytime minimum cannot be greater than maximum.")
    study_categories = values_for("studytime")
    if study_categories:
        try:
            category_values = {float(value) for value in study_categories}
        except ValueError as error:
            raise ValueError("Unsupported study-time category.") from error
        values = pd.to_numeric(filtered["studytime"], errors="coerce")
        filtered = filtered[values.isin(category_values)]
        state["studytime"] = study_categories
    elif study_min is not None or study_max is not None:
        values = pd.to_numeric(filtered["studytime"], errors="coerce")
        if study_min is not None:
            filtered = filtered[values >= study_min]
        if study_max is not None:
            filtered = filtered[values <= study_max]
        state["studytime_min"] = study_min
        state["studytime_max"] = study_max

    absence_groups = values_for("absence_group")
    if absence_groups:
        matchers = {
            "none": lambda values: values == 0,
            "low": lambda values: (values >= 1) & (values <= 5),
            "moderate": lambda values: (values >= 6) & (values <= 10),
            "high": lambda values: values > 10,
        }
        if any(group not in matchers for group in absence_groups):
            raise ValueError("Unsupported absence category.")
        values = pd.to_numeric(filtered["absences"], errors="coerce")
        mask = pd.Series(False, index=filtered.index)
        for group in absence_groups:
            mask = mask | matchers[group](values)
        filtered = filtered[mask]
        state["absence_group"] = absence_groups

    return filtered, state


def assessment_scatter_data(records: pd.DataFrame, assessment_field: str) -> list[dict]:
    """Return paired assessment/G3 points without exposing student identities."""
    if assessment_field not in records or "g3" not in records:
        return []
    paired = pd.DataFrame({
        "assessment": pd.to_numeric(records[assessment_field], errors="coerce"),
        "g3": pd.to_numeric(records["g3"], errors="coerce"),
    }).dropna()
    return [{"assessment": float(row.assessment), "g3": float(row.g3)} for row in paired.itertuples(index=False)]


def retrieve_dataset_records(dataset: Dataset) -> pd.DataFrame:
    """Retrieve only records belonging to ``dataset`` in stable row order."""
    records = (
        StudentRecord.query
        .filter(StudentRecord.dataset_id == dataset.id)
        .order_by(StudentRecord.student)
        .all()
    )
    return pd.DataFrame(
        [
            {column: getattr(record, column) for column in ANALYSIS_COLUMNS}
            for record in records
        ],
        columns=list(ANALYSIS_COLUMNS),
    )


def _numeric_series(frame: pd.DataFrame, column: str) -> pd.Series:
    """Coerce a field for analysis without converting invalid values to zero."""
    return pd.to_numeric(frame[column], errors="coerce")


def prepare_analysis_input(dataset: Dataset) -> AnalysisInput:
    """Prepare temporary analysis data and complete-dataset quality metrics."""
    frame = retrieve_dataset_records(dataset).copy()
    for column in ("g1", "g2", "g3", "studytime", "absences"):
        frame[column] = _numeric_series(frame, column)

    valid_g3 = frame["g3"].notna()
    quality = DatasetQuality(
        total_records=len(frame),
        valid_g3_records=int(valid_g3.sum()),
        excluded_records=int((~valid_g3).sum()),
        missing_g1=(int(frame["g1"].isna().sum()) if dataset.g1_label else None),
        missing_g2=(int(frame["g2"].isna().sum()) if dataset.g2_label else None),
        missing_studytime=int(frame["studytime"].isna().sum()),
        missing_absences=int(frame["absences"].isna().sum()),
    )
    return AnalysisInput(dataset=dataset, records=frame, quality=quality)


def _valid_grades(records: pd.DataFrame) -> pd.Series:
    """Return valid G3 values without changing the source frame."""
    return pd.to_numeric(records["g3"], errors="coerce").dropna()


def calculate_grade_statistics(records: pd.DataFrame) -> GradeStatistics:
    """Calculate approved descriptive statistics for G3."""
    values = _valid_grades(records)
    if values.empty:
        return GradeStatistics(0, None, None, None, None, None, None, None)
    return GradeStatistics(
        count=int(values.size),
        mean=float(values.mean()),
        median=float(values.median()),
        minimum=float(values.min()),
        maximum=float(values.max()),
        population_stddev=float(values.std(ddof=0)),
        q1=float(values.quantile(0.25, interpolation="linear")),
        q3=float(values.quantile(0.75, interpolation="linear")),
    )


def _band_definitions(grade_scale_max: float):
    """Return project bands scaled to the configured grade maximum."""
    if grade_scale_max == 20:
        return [
            ("Very low", 0, 5, False),
            ("Low", 5, 9, False),
            ("Moderate", 9, 13, False),
            ("Good", 13, 17, False),
            ("High", 17, 20, True),
        ]
    proportions = ((0, 0.25), (0.25, 0.45), (0.45, 0.65), (0.65, 0.85), (0.85, 1.0))
    labels = ("Very low", "Low", "Moderate", "Good", "High")
    return [
        (label, grade_scale_max * lower, grade_scale_max * upper, index == 4)
        for index, (label, (lower, upper)) in enumerate(zip(labels, proportions))
    ]


def calculate_grade_distribution(records: pd.DataFrame, grade_scale_max: float) -> list[GradeBand]:
    """Assign every valid G3 value to exactly one configured-scale band."""
    values = _valid_grades(records)
    total = int(values.size)
    bands = []
    for label, lower, upper, include_upper in _band_definitions(float(grade_scale_max)):
        if include_upper:
            matches = values[(values >= lower) & (values <= upper)]
        else:
            matches = values[(values >= lower) & (values < upper)]
        count = int(matches.size)
        bands.append(GradeBand(
            label=label,
            lower=float(lower),
            upper=float(upper),
            include_upper=include_upper,
            count=count,
            percentage=(count / total * 100) if total else 0.0,
        ))
    return bands


def calculate_assessment_summaries(records: pd.DataFrame, assessment_fields=("g1", "g2", "g3")) -> list[AssessmentSummary]:
    """Summarize available assessments and paired G3 differences."""
    summaries = []
    g3 = _valid_grades(records)
    for field in assessment_fields:
        if field not in records:
            continue
        values = pd.to_numeric(records[field], errors="coerce")
        valid = values.dropna()
        paired = pd.concat([values.rename("assessment"), records["g3"].rename("g3")], axis=1).dropna()
        difference = (paired["g3"] - paired["assessment"]).mean() if not paired.empty else None
        summaries.append(AssessmentSummary(
            field=field,
            count=int(valid.size),
            mean=float(valid.mean()) if not valid.empty else None,
            paired_count_with_g3=int(len(paired)),
            mean_paired_difference_from_g3=float(difference) if difference is not None else None,
        ))
    return summaries


def _group_summary(records: pd.DataFrame, field: str, definitions) -> list[AnalysisGroup]:
    values = pd.to_numeric(records[field], errors="coerce")
    g3 = pd.to_numeric(records["g3"], errors="coerce")
    result = []
    for label, matcher in definitions:
        selected = g3[matcher(values) & g3.notna()]
        result.append(AnalysisGroup(label, int(selected.size), float(selected.mean()) if not selected.empty else None))
    return result


def calculate_studytime_analysis(records: pd.DataFrame, categorical: bool = False) -> dict:
    """Group study time without treating categorical codes as measured hours."""
    if "studytime" not in records or pd.to_numeric(records["studytime"], errors="coerce").dropna().empty:
        return {"available": False, "categorical": categorical, "groups": [], "average": None}
    if categorical:
        values = pd.to_numeric(records["studytime"], errors="coerce")
        g3 = pd.to_numeric(records["g3"], errors="coerce")
        category_labels = {1: "Less than 2 hours/week", 2: "2–5 hours/week", 3: "5–10 hours/week", 4: "More than 10 hours/week"}
        groups = [AnalysisGroup(category_labels.get(int(category), f"Category {category}"), int((values == category).where(g3.notna(), False).sum()), float(g3[(values == category) & g3.notna()].mean()) if ((values == category) & g3.notna()).any() else None) for category in sorted(values.dropna().unique())]
        return {"available": True, "categorical": True, "groups": groups, "average": None}
    definitions = [
        ("0–5 hours/week", lambda values: (values >= 0) & (values <= 5)),
        ("Above 5–10 hours/week", lambda values: (values > 5) & (values <= 10)),
        ("Above 10–15 hours/week", lambda values: (values > 10) & (values <= 15)),
        ("Above 15 hours/week", lambda values: values > 15),
    ]
    values = pd.to_numeric(records["studytime"], errors="coerce")
    return {"available": True, "categorical": False, "groups": _group_summary(records, "studytime", definitions), "average": float(values.mean())}


def calculate_absence_analysis(records: pd.DataFrame) -> dict:
    """Group verified absence values and summarize valid G3 performance."""
    if "absences" not in records:
        return {"available": False, "groups": [], "average": None}
    values = pd.to_numeric(records["absences"], errors="coerce")
    if values.dropna().empty:
        return {"available": False, "groups": [], "average": None}
    definitions = [
        ("No absences (0 days)", lambda column: column == 0),
        ("Low (1–5 days)", lambda column: (column >= 1) & (column <= 5)),
        ("Moderate (6–10 days)", lambda column: (column >= 6) & (column <= 10)),
        ("High (more than 10 days)", lambda column: column > 10),
    ]
    return {"available": True, "groups": _group_summary(records, "absences", definitions), "average": float(values.mean())}


def calculate_correlation(records: pd.DataFrame, x_field: str, y_field: str = "g3") -> CorrelationResult:
    """Calculate exploratory Pearson correlation with minimum safeguards."""
    if x_field not in records or y_field not in records:
        return CorrelationResult(x_field, y_field, 0, None, False)
    paired = pd.DataFrame({"x": pd.to_numeric(records[x_field], errors="coerce"), "y": pd.to_numeric(records[y_field], errors="coerce")}).dropna()
    count = len(paired)
    if count < 3 or paired["x"].nunique() <= 1 or paired["y"].nunique() <= 1:
        return CorrelationResult(x_field, y_field, count, None, False)
    coefficient = float(paired["x"].corr(paired["y"]))
    return CorrelationResult(x_field, y_field, count, coefficient, count >= 10)


def build_statistical_findings(statistics: GradeStatistics, distribution: list[GradeBand], groups: list[AnalysisGroup], correlation: CorrelationResult | None = None) -> list[StatisticalFinding]:
    """Build deterministic observations without causal or individual claims."""
    findings = []
    if statistics.mean is not None:
        findings.append(StatisticalFinding("average", f"The average final grade is {statistics.mean:.2f}."))
    if distribution and statistics.count:
        largest = max(distribution, key=lambda band: band.count)
        findings.append(StatisticalFinding("grade_distribution", f"The largest grade group is {largest.label} ({largest.count} students)."))
    eligible = [group for group in groups if group.count >= 3 and group.average_g3 is not None]
    if len(eligible) >= 2:
        highest, lowest = max(eligible, key=lambda group: group.average_g3), min(eligible, key=lambda group: group.average_g3)
        if highest.average_g3 - lowest.average_g3 >= 1:
            findings.append(StatisticalFinding("group_difference", f"{highest.label} has a higher average final grade than {lowest.label} by {highest.average_g3 - lowest.average_g3:.2f} points."))
    if correlation and correlation.interpretation_eligible and correlation.coefficient is not None and abs(correlation.coefficient) >= 0.30:
        direction = "positive" if correlation.coefficient >= 0.30 else "negative"
        findings.append(StatisticalFinding("correlation", f"There is a {direction} linear association between {correlation.x_field} and {correlation.y_field} (r={correlation.coefficient:.2f})."))
    return findings
