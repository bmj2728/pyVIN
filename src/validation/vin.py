import re
from src.exceptions import InvalidVINError

VIN_PATTERN = re.compile(r'^[A-HJ-NPR-Z0-9*]{17}$')  # * allowed for wildcards in api


def validate_and_normalize_vin(vin: str) -> str:
    """Validate and normalize VIN. Returns uppercase VIN."""
    if not vin:
        raise InvalidVINError("VIN cannot be empty")

    normalized = vin.upper().strip()

    if not VIN_PATTERN.match(normalized):
        raise InvalidVINError(
            f"Invalid VIN format: {vin}. "
            "Must be 17 characters (A-Z, 0-9, * allowed, no I, O, or Q)"
        )

    return normalized

__all__ = ["validate_and_normalize_vin"]