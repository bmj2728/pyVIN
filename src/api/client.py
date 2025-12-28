from functools import lru_cache
import requests
from src.api.models import VINDecodeResult
from src.config import *
from src.exceptions import APIError, NetworkError
from src.validation.vin import validate_and_normalize_vin


@lru_cache(maxsize=CACHE_SIZE)
def decode_vin_values_extended(vin: str) -> VINDecodeResult:
    """Decode VIN using NHTSA API. Returns Pydantic model."""
    normalized_vin = validate_and_normalize_vin(vin)

    url = f"{NHTSA_BASE_URL}/{DECODE_VIN_EXT_ENDPOINT}/{normalized_vin}"
    params = {"format": DEFAULT_FORMAT}

    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise NetworkError(f"Failed to reach NHTSA API: {e}")

    data = resp.json()

    if not data.get("Results"):
        raise APIError("No results returned from API")

    result = VINDecodeResult(**data["Results"][0])

    if result.error_code and result.error_code != "0":
        raise APIError(f"API Error: {result.error_text}")

    return result