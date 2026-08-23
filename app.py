"""
app.py
======
Ekalavya — AI-Powered Educational Assessment Platform
Flask application entry point.

Routes
------
GET  /               → Home / landing page
GET  /assessment     → Student assessment form
POST /predict        → Process form → call IBM watsonx ML → redirect to result
GET  /result         → Prediction result page
GET  /health         → Health-check endpoint (for Docker / IBM Cloud)
"""

import os
import logging
from datetime import datetime, timezone

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    flash,
)
from dotenv import load_dotenv

from utils.ibm_wml import predict

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-insecure-key-change-me")

# ---------------------------------------------------------------------------
# Field definitions (ordered — must match model input schema)
# ---------------------------------------------------------------------------
MODEL_FIELDS = [
    "student_id",
    "age",
    "gender",
    "class_grade",
    "school_type",
    "attendance_percentage",
    "math_score",
    "science_score",
    "english_score",
    "social_science_score",
    "previous_grade_percentage",
    "study_hours_per_day",
    "homework_completion",
    "learning_difficulty",
    "internet_access",
    "digital_device",
    "parent_education",
    "parent_occupation",
    "annual_family_income",
    "family_size",
    "distance_to_school_km",
    "transportation",
    "scholarship_received",
    "mentoring_support",
    "extracurricular_participation",
    "health_issue",
    "dropout_history_in_family",
    "motivation_level",
    "teacher_assessment",
]

# Numeric fields that must be cast to float
NUMERIC_FIELDS = {
    "age",
    "attendance_percentage",
    "math_score",
    "science_score",
    "english_score",
    "social_science_score",
    "previous_grade_percentage",
    "study_hours_per_day",
    "annual_family_income",
    "family_size",
    "distance_to_school_km",
}

# Validation rules: (min, max) for numeric fields
NUMERIC_RANGES = {
    "age": (3, 25),
    "attendance_percentage": (0, 100),
    "math_score": (0, 100),
    "science_score": (0, 100),
    "english_score": (0, 100),
    "social_science_score": (0, 100),
    "previous_grade_percentage": (0, 100),
    "study_hours_per_day": (0, 24),
    "annual_family_income": (0, 10_000_000),
    "family_size": (1, 20),
    "distance_to_school_km": (0, 200),
}

# ---------------------------------------------------------------------------
# Label encoding maps for categorical fields
# ---------------------------------------------------------------------------
# Each map encodes the string category → integer exactly as sklearn
# LabelEncoder (alphabetical sort → 0-based index) would produce during
# training. These MUST match the encoding used when the model was trained.
# ---------------------------------------------------------------------------
LABEL_ENCODINGS: dict[str, dict[str, int]] = {
    # student_id is a free-text identifier — passed as-is (string)
    "gender": {
        "Female": 0,
        "Male":   1,
        "Other":  2,
    },
    "class_grade": {
        "Grade 1":  0,
        "Grade 10": 1,
        "Grade 11": 2,
        "Grade 12": 3,
        "Grade 2":  4,
        "Grade 3":  5,
        "Grade 4":  6,
        "Grade 5":  7,
        "Grade 6":  8,
        "Grade 7":  9,
        "Grade 8":  10,
        "Grade 9":  11,
    },
    "school_type": {
        "Government":   0,
        "Private":      1,
        "Semi-Private": 2,
    },
    "homework_completion": {
        "Always":    0,
        "Never":     1,
        "Rarely":    2,
        "Sometimes": 3,
        "Usually":   4,
    },
    "learning_difficulty": {
        "Mild":     0,
        "Moderate": 1,
        "None":     2,
        "Severe":   3,
    },
    "internet_access": {
        "No":  0,
        "Yes": 1,
    },
    "digital_device": {
        "Desktop":    0,
        "Laptop":     1,
        "None":       2,
        "Smartphone": 3,
        "Tablet":     4,
    },
    "parent_education": {
        "Graduate":            0,
        "Higher Secondary":    1,
        "No Formal Education": 2,
        "Post Graduate":       3,
        "Primary":             4,
        "Secondary":           5,
    },
    "parent_occupation": {
        "Business":          0,
        "Daily Wage Worker": 1,
        "Farmer":            2,
        "Post Graduate":     3,
        "Professional":      4,
        "Salaried":          5,
        "Self Employed":     6,
        "Skilled Worker":    7,
        "Unemployed":        8,
    },
    "transportation": {
        "Auto Rickshaw":   0,
        "Bicycle":         1,
        "Personal Vehicle":2,
        "Public Bus":      3,
        "School Bus":      4,
        "Walking":         5,
    },
    "scholarship_received": {
        "No":  0,
        "Yes": 1,
    },
    "mentoring_support": {
        "No":  0,
        "Yes": 1,
    },
    "extracurricular_participation": {
        "No":  0,
        "Yes": 1,
    },
    "health_issue": {
        "Chronic":  0,
        "Minor":    1,
        "Moderate": 2,
        "None":     3,
    },
    "dropout_history_in_family": {
        "No":  0,
        "Yes": 1,
    },
    "motivation_level": {
        "High":      0,
        "Low":       1,
        "Medium":    2,
        "Very High": 3,
        "Very Low":  4,
    },
    "teacher_assessment": {
        "Average":       0,
        "Below Average": 1,
        "Excellent":     2,
        "Good":          3,
        "Poor":          4,
    },
}

# Human-readable labels for the result summary
FIELD_LABELS = {
    "student_id": "Student ID",
    "age": "Age",
    "gender": "Gender",
    "class_grade": "Class / Grade",
    "school_type": "School Type",
    "attendance_percentage": "Attendance (%)",
    "math_score": "Math Score",
    "science_score": "Science Score",
    "english_score": "English Score",
    "social_science_score": "Social Science Score",
    "previous_grade_percentage": "Previous Grade (%)",
    "study_hours_per_day": "Study Hours / Day",
    "homework_completion": "Homework Completion",
    "learning_difficulty": "Learning Difficulty",
    "internet_access": "Internet Access",
    "digital_device": "Digital Device",
    "parent_education": "Parent Education",
    "parent_occupation": "Parent Occupation",
    "annual_family_income": "Annual Family Income",
    "family_size": "Family Size",
    "distance_to_school_km": "Distance to School (km)",
    "transportation": "Transportation Mode",
    "scholarship_received": "Scholarship Received",
    "mentoring_support": "Mentoring Support",
    "extracurricular_participation": "Extracurricular Participation",
    "health_issue": "Health Issue",
    "dropout_history_in_family": "Dropout History in Family",
    "motivation_level": "Motivation Level",
    "teacher_assessment": "Teacher Assessment",
}


# ---------------------------------------------------------------------------
# Validation helper
# ---------------------------------------------------------------------------

def _validate_and_parse(form: dict) -> tuple[list, dict]:
    """
    Validate every submitted form field and build the ordered values list.

    Returns
    -------
    tuple[list, dict]
        (ordered_values, errors_dict)
        If errors_dict is non-empty, the values list should not be used.
    """
    values = []
    errors = {}

    for field in MODEL_FIELDS:
        raw = form.get(field, "").strip()

        # Required check
        if raw == "":
            errors[field] = f"{FIELD_LABELS.get(field, field)} is required."
            values.append(None)
            continue

        # Numeric fields — cast to float and range-check
        if field in NUMERIC_FIELDS:
            try:
                val = float(raw)
            except ValueError:
                errors[field] = (
                    f"{FIELD_LABELS.get(field, field)} must be a valid number."
                )
                values.append(None)
                continue

            lo, hi = NUMERIC_RANGES.get(field, (None, None))
            if lo is not None and not (lo <= val <= hi):
                errors[field] = (
                    f"{FIELD_LABELS.get(field, field)} must be between {lo} and {hi}."
                )
                values.append(None)
                continue

            values.append(val)

        # Categorically encoded fields — map string → integer
        elif field in LABEL_ENCODINGS:
            encoding_map = LABEL_ENCODINGS[field]
            if raw not in encoding_map:
                errors[field] = (
                    f"{FIELD_LABELS.get(field, field)}: "
                    f"'{raw}' is not a recognised option."
                )
                values.append(None)
                continue
            values.append(encoding_map[raw])

        # Free-text fields (e.g. student_id) — pass as string
        else:
            values.append(raw)

    return values, errors


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Home / landing page."""
    return render_template("index.html")


@app.route("/assessment")
def assessment():
    """Student assessment form."""
    return render_template("assessment.html")


@app.route("/predict", methods=["POST"])
def predict_route():
    """
    Validate form → call IBM watsonx ML → store result in session → redirect.
    """
    form_data = request.form.to_dict()

    # --- Validate -----------------------------------------------------------
    values, errors = _validate_and_parse(form_data)

    if errors:
        # Re-render form with errors and previously entered values
        return render_template(
            "assessment.html",
            errors=errors,
            form_data=form_data,
        )

    # --- Build human-readable summary for the result page ------------------
    summary = {
        FIELD_LABELS[field]: (
            f"{form_data.get(field, '')}"   # always store the original string for display
        )
        for field in MODEL_FIELDS
    }

    # --- Build raw numeric values dict for charts --------------------------
    # Stores original form string values keyed by field name for JS charts
    raw_values = {field: form_data.get(field, "") for field in MODEL_FIELDS}

    # --- Call IBM watsonx ML -----------------------------------------------
    try:
        result = predict(MODEL_FIELDS, values)
    except RuntimeError as exc:
        logger.error("Prediction error: %s", exc)
        return render_template(
            "assessment.html",
            errors={"__api__": str(exc)},
            form_data=form_data,
        )
    except Exception as exc:  # pragma: no cover
        logger.exception("Unexpected error during prediction: %s", exc)
        return render_template(
            "assessment.html",
            errors={
                "__api__": (
                    "An unexpected error occurred while contacting the AI model. "
                    "Please try again."
                )
            },
            form_data=form_data,
        )

    # --- Store ephemeral result in session (auto-cleared after display) -----
    session["prediction"]  = result["prediction"]
    session["confidence"]  = result["confidence"]
    session["summary"]     = summary
    session["raw_values"]  = raw_values
    session["timestamp"]   = datetime.now(timezone.utc).strftime("%B %d, %Y  %H:%M UTC")

    return redirect(url_for("result"))


@app.route("/result")
def result():
    """Prediction result page."""
    prediction = session.pop("prediction", None)

    if prediction is None:
        # Direct navigation without a prediction — redirect to form
        return redirect(url_for("assessment"))

    confidence  = session.pop("confidence",  None)
    summary     = session.pop("summary",     {})
    raw_values  = session.pop("raw_values",  {})
    timestamp   = session.pop("timestamp",   "")

    return render_template(
        "result.html",
        prediction=prediction,
        confidence=confidence,
        summary=summary,
        raw_values=raw_values,
        timestamp=timestamp,
    )


@app.route("/health")
def health():
    """Lightweight health-check endpoint."""
    return jsonify({"status": "ok", "service": "Ekalavya"}), 200


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(exc):
    return render_template("index.html"), 404


@app.errorhandler(500)
def internal_error(exc):
    logger.error("Internal server error: %s", exc)
    return render_template(
        "assessment.html",
        errors={
            "__api__": "An internal server error occurred. Please try again."
        },
    ), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )