"""AQI-related utility helpers."""


def color_from_aqi(aqi: float) -> list[int]:
    """
    Return RGB color for AQI bucket.

    Buckets are aligned to the existing app behavior.
    """
    if aqi <= 50:
        return [0, 255, 0]
    if aqi <= 100:
        return [255, 255, 0]
    if aqi <= 200:
        return [255, 165, 0]
    if aqi <= 300:
        return [255, 0, 0]
    return [128, 0, 128]
