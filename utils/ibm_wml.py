"""
utils/ibm_wml.py
================
IBM watsonx Machine Learning REST API client for Ekalavya.

Responsibilities:
  - Authenticate with IBM Cloud IAM to obtain a Bearer token.
  - Send a prediction request to the deployed watsonx ML scoring endpoint.
  - Parse and return the prediction result.
  - Handle and surface meaningful errors without exposing credentials.
"""

import os
import logging
from typing import Any

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------------
load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
IAM_GRANT_TYPE = "urn:ibm:params:oauth:grant-type:apikey"

# Expected prediction labels returned by the deployed model
VALID_PREDICTIONS = {"On Track", "At Risk", "Dropout"}


# ---------------------------------------------------------------------------
# IAM Token
# ---------------------------------------------------------------------------

def _get_iam_token(api_key: str) -> str:
    """
    Exchange an IBM Cloud API key for a short-lived IAM Bearer token.

    Parameters
    ----------
    api_key : str
        IBM Cloud API key loaded from environment.

    Returns
    -------
    str
        The IAM access token string.

    Raises
    ------
    RuntimeError
        If the token request fails for any reason.
    """
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "grant_type": IAM_GRANT_TYPE,
        "apikey": api_key,
    }

    try:
        response = requests.post(
            IAM_TOKEN_URL,
            headers=headers,
            data=payload,
            timeout=30,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError(
            "IBM IAM token request timed out. "
            "Please check your network connection and try again."
        )
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Unable to reach IBM IAM service. "
            "Please verify your internet connection."
        )
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        raise RuntimeError(
            f"IBM IAM authentication failed (HTTP {status}). "
            "Please verify your IBM_API_KEY in the .env file."
        )

    token_data = response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise RuntimeError(
            "IBM IAM response did not contain an access token. "
            "Please check your IBM_API_KEY."
        )

    return access_token


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------

def predict(input_fields: list[str], input_values: list[Any]) -> dict:
    """
    Call the deployed IBM watsonx Machine Learning scoring endpoint and
    return a structured prediction result.

    Parameters
    ----------
    input_fields : list[str]
        Ordered list of feature names expected by the model.
    input_values : list[Any]
        Ordered list of feature values corresponding to ``input_fields``.

    Returns
    -------
    dict
        {
            "prediction"       : str,   # "On Track" | "At Risk" | "Dropout"
            "confidence"       : float | None,
            "raw_response"     : dict,
        }

    Raises
    ------
    RuntimeError
        Descriptive error message safe to display to the end user.
    """
    # ------------------------------------------------------------------ #
    # 1. Load credentials from environment
    # ------------------------------------------------------------------ #
    api_key = os.getenv("IBM_API_KEY", "").strip()
    wml_url = os.getenv("IBM_WML_URL", "").strip().rstrip("/")
    space_id = os.getenv("IBM_SPACE_ID", "").strip()
    deployment_id = os.getenv("IBM_DEPLOYMENT_ID", "").strip()

    missing = [
        name for name, val in [
            ("IBM_API_KEY", api_key),
            ("IBM_WML_URL", wml_url),
            ("IBM_SPACE_ID", space_id),
            ("IBM_DEPLOYMENT_ID", deployment_id),
        ]
        if not val
    ]
    if missing:
        raise RuntimeError(
            f"Missing required IBM configuration: {', '.join(missing)}. "
            "Please update the .env file."
        )

    # ------------------------------------------------------------------ #
    # 2. Obtain IAM Bearer token
    # ------------------------------------------------------------------ #
    logger.info("Requesting IBM IAM access token …")
    iam_token = _get_iam_token(api_key)

    # ------------------------------------------------------------------ #
    # 3. Build scoring endpoint URL
    # ------------------------------------------------------------------ #
    scoring_url = (
        f"{wml_url}/ml/v4/deployments/{deployment_id}/predictions"
        f"?version=2021-05-01&space_id={space_id}"
    )

    # ------------------------------------------------------------------ #
    # 4. Build request payload
    # ------------------------------------------------------------------ #
    payload = {
        "input_data": [
            {
                "fields": input_fields,
                "values": [input_values],
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # ------------------------------------------------------------------ #
    # 5. Call the scoring endpoint
    # ------------------------------------------------------------------ #
    logger.info("Calling IBM watsonx ML scoring endpoint …")
    try:
        response = requests.post(
            scoring_url,
            json=payload,
            headers=headers,
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError(
            "The IBM watsonx ML model request timed out. "
            "Please try again in a moment."
        )
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Unable to reach the IBM watsonx ML service. "
            "Please check your IBM_WML_URL and network connection."
        )
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        try:
            detail = exc.response.json()
        except Exception:
            detail = {}
        error_msg = detail.get("errors", [{}])[0].get("message", "") if detail else ""
        raise RuntimeError(
            f"IBM watsonx ML scoring failed (HTTP {status}). "
            + (f"Details: {error_msg}" if error_msg else "Please check your deployment credentials.")
        )

    # ------------------------------------------------------------------ #
    # 6. Parse the response
    # ------------------------------------------------------------------ #
    raw = response.json()
    logger.debug("Raw WML response: %s", raw)

    prediction, confidence = _extract_prediction(raw)

    return {
        "prediction": prediction,
        "confidence": confidence,
        "raw_response": raw,
    }


# ---------------------------------------------------------------------------
# Response Parser
# ---------------------------------------------------------------------------

def _extract_prediction(raw: dict) -> tuple[str, float | None]:
    """
    Extract the prediction label and optional confidence score from the
    raw IBM watsonx ML API response.

    The standard watsonx ML scoring response has the structure:

    {
      "predictions": [
        {
          "fields": ["prediction", "probability"],
          "values": [["On Track", [0.15, 0.72, 0.13]]]
        }
      ]
    }

    Parameters
    ----------
    raw : dict
        The full JSON response from the scoring endpoint.

    Returns
    -------
    tuple[str, float | None]
        (prediction_label, confidence_score_or_None)

    Raises
    ------
    RuntimeError
        If the response cannot be parsed.
    """
    try:
        predictions_list = raw.get("predictions", [])
        if not predictions_list:
            raise ValueError("'predictions' key missing or empty.")

        result_block = predictions_list[0]
        fields: list[str] = result_block.get("fields", [])
        values: list = result_block.get("values", [[]])
        row: list = values[0] if values else []

        if not row:
            raise ValueError("Prediction values array is empty.")

        # --- Locate prediction label -----------------------------------
        prediction_label: str | None = None
        confidence: float | None = None

        # Strategy 1: explicit "prediction" field
        if "prediction" in fields:
            idx = fields.index("prediction")
            prediction_label = str(row[idx]).strip()

        # Strategy 2: first string value in the row
        if prediction_label is None:
            for item in row:
                if isinstance(item, str):
                    prediction_label = item.strip()
                    break

        # Strategy 3: first element
        if prediction_label is None:
            prediction_label = str(row[0]).strip()

        # Normalise common variations
        normalise_map = {
            "on track": "On Track",
            "at risk": "At Risk",
            "dropout": "Dropout",
        }
        prediction_label = normalise_map.get(
            prediction_label.lower(), prediction_label
        )

        if prediction_label not in VALID_PREDICTIONS:
            logger.warning(
                "Unexpected prediction label from model: '%s'. "
                "Accepted as-is.",
                prediction_label,
            )

        # --- Locate confidence / probability ---------------------------
        if "probability" in fields:
            prob_idx = fields.index("probability")
            prob_val = row[prob_idx]
            if isinstance(prob_val, (list, tuple)) and prob_val:
                confidence = round(float(max(prob_val)) * 100, 1)
            elif isinstance(prob_val, (int, float)):
                confidence = round(float(prob_val) * 100, 1)

        return prediction_label, confidence

    except (KeyError, IndexError, TypeError, ValueError) as exc:
        logger.error("Failed to parse WML response: %s | raw=%s", exc, raw)
        raise RuntimeError(
            "Received an unexpected response format from the IBM watsonx ML model. "
            "Please verify that the deployed model returns 'prediction' in its output fields."
        )
