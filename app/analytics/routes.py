"""Academic Analytics Dashboard routes."""

from dataclasses import asdict
from datetime import datetime
from io import BytesIO

from flask import abort, render_template, request, send_file
from werkzeug.utils import secure_filename

from app.analytics import analytics_bp
from app.analytics.services import (
    build_statistical_findings,
    calculate_absence_analysis,
    calculate_assessment_summaries,
    calculate_correlation,
    calculate_grade_distribution,
    calculate_grade_statistics,
    calculate_studytime_analysis,
    assessment_scatter_data,
    prepare_analysis_input,
    apply_filters,
    filtered_records_csv,
)
from app.auth.decorators import role_required
from app.datasets.routes import accessible_dataset_or_404, active_dataset_for_current_user


@analytics_bp.route("/", methods=["GET"])
@role_required("admin", "educator")
def dashboard():
    dataset = active_dataset_for_current_user()
    if dataset is None:
        abort(404)
    return _render_dashboard(dataset, request.args)


@analytics_bp.route("/<int:dataset_id>", methods=["GET"])
@role_required("admin", "educator")
def dataset_dashboard(dataset_id):
    dataset = accessible_dataset_or_404(dataset_id)
    return _render_dashboard(dataset, request.args)


@analytics_bp.route("/<int:dataset_id>/export", methods=["GET"])
@role_required("admin", "educator")
def export_dataset(dataset_id):
    """Download the authorized dataset records matching active filters."""
    dataset = accessible_dataset_or_404(dataset_id)
    analysis = prepare_analysis_input(dataset)
    try:
        filtered_records, _ = apply_filters(
            analysis.records, request.args, dataset.grade_scale_max
        )
    except ValueError as error:
        abort(400, description=str(error))

    dataset_name = secure_filename(dataset.name or "dataset") or "dataset"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analytics_{dataset_name}_{dataset.id}_{timestamp}.csv"
    return send_file(
        BytesIO(filtered_records_csv(filtered_records)),
        mimetype="text/csv; charset=utf-8",
        as_attachment=True,
        download_name=filename,
    )


def _render_dashboard(dataset, filter_params=None):
    analysis = prepare_analysis_input(dataset)
    try:
        filtered_records, filters = apply_filters(analysis.records, filter_params or {}, dataset.grade_scale_max)
    except ValueError as error:
        abort(400, description=str(error))
    statistics = calculate_grade_statistics(filtered_records)
    distribution = calculate_grade_distribution(filtered_records, dataset.grade_scale_max)
    assessments = calculate_assessment_summaries(filtered_records)
    assessment_labels = {"g1": dataset.g1_label or "G1", "g2": dataset.g2_label or "G2", "g3": dataset.g3_label or "G3"}
    assessments = [{**asdict(item), "label": assessment_labels.get(item.field, item.field.upper())} for item in assessments]
    largest_band = max(distribution, key=lambda band: band.count) if distribution and analysis.quality.valid_g3_records else None
    band_counts = {band.label: band.count for band in distribution}
    source_name = (dataset.source_filename or "").lower()
    studytime_values = filtered_records["studytime"].dropna().tolist()
    uci_source = "uci" in source_name or "student-mat" in source_name or "student-por" in source_name
    studytime_categorical = uci_source and bool(studytime_values) and all(float(value).is_integer() and int(value) in {1, 2, 3, 4} for value in studytime_values)
    studytime_options = sorted({int(value) for value in studytime_values if float(value).is_integer()}) if studytime_categorical else []
    grade_options = [value for value in range(int(dataset.grade_scale_max) + 1)]
    studytime_numeric_options = sorted({float(value) for value in studytime_values}) if not studytime_categorical else []
    studytime = calculate_studytime_analysis(filtered_records, categorical=studytime_categorical)
    absences = calculate_absence_analysis(filtered_records)
    correlations = []
    if studytime["available"] and not studytime["categorical"]:
        correlations.append(calculate_correlation(filtered_records, "studytime"))
    if absences["available"]:
        correlations.append(calculate_correlation(filtered_records, "absences"))
    findings = build_statistical_findings(statistics, distribution, absences["groups"], correlations[0] if correlations else None)
    selected_assessment = next((field for field in ("g1", "g2", "g3") if f"{field}_min" in filters or f"{field}_max" in filters), "g3")
    return render_template(
        "analytics/dashboard.html",
        dataset=dataset,
        active_dataset=dataset,
        quality=asdict(analysis.quality),
        statistics=asdict(statistics),
        distribution=[asdict(item) for item in distribution],
        assessments=assessments,
        assessment_scatter={"g1": assessment_scatter_data(filtered_records, "g1"), "g2": assessment_scatter_data(filtered_records, "g2")},
        assessment_options=[{"field": field, "label": assessment_labels[field]} for field in ("g1", "g2", "g3") if field == "g3" or getattr(dataset, f"{field}_label")],
        selected_assessment=selected_assessment,
        performance_label=largest_band.label if largest_band else None,
        good_count=band_counts.get("Good", 0) + band_counts.get("High", 0),
        lower_count=band_counts.get("Very low", 0) + band_counts.get("Low", 0),
        studytime={**studytime, "groups": [asdict(item) for item in studytime["groups"]]},
        absences={**absences, "groups": [asdict(item) for item in absences["groups"]]},
        correlations=[asdict(item) for item in correlations],
        findings=[asdict(item) for item in findings],
        filters=filters,
        filtered_count=len(filtered_records),
        studytime_categorical=studytime_categorical,
        studytime_options=studytime_options,
        grade_options=grade_options,
        studytime_numeric_options=studytime_numeric_options,
    )
