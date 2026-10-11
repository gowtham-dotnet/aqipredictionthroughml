"""JSON utility helpers for the Streamlit AQI app."""

import json
import math
from typing import Any


def safe_json_dumps(obj: Any) -> str:
    """
    Serialize a Python object to JSON after replacing NaN float values with null.

    This keeps frontend JSON parsing safe for map payloads that may contain NaN.
    """

    def _clean(value: Any) -> Any:
        if isinstance(value, float) and math.isnan(value):
            return None
        if isinstance(value, dict):
            return {k: _clean(v) for k, v in value.items()}
        if isinstance(value, list):
            return [_clean(v) for v in value]
        return value

    return json.dumps(_clean(obj))
