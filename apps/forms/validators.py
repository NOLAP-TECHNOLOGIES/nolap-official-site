import re

from django.core.exceptions import ValidationError


def validate_ghana_phone(value):
    """Validate Ghana phone number: +233XXXXXXXXX or 0XXXXXXXXX (10 digits)."""
    cleaned = re.sub(r"[\s\-()]", "", value)
    if cleaned.startswith("+233"):
        cleaned = "0" + cleaned[4:]
    if cleaned.startswith("233"):
        cleaned = "0" + cleaned[3:]
    if not re.match(r"^0[235]\d{8}$", cleaned):
        raise ValidationError(
            "Enter a valid Ghana phone number (e.g. 024 123 4567 or +233 24 123 4567)."
        )


def validate_ghana_card(value):
    """Validate Ghana Card number: GHA-XXXXXXXXX-X."""
    if not re.match(r"^GHA-\d{9}-\d$", value.upper().strip()):
        raise ValidationError(
            "Enter a valid Ghana Card number (e.g. GHA-123456789-0)."
        )


def validate_digital_address(value):
    """Validate GhanaPost digital address: XX-XXX-XXXX."""
    if not re.match(r"^[A-Z]{2}-\d{3,4}-\d{4}$", value.upper().strip()):
        raise ValidationError(
            "Enter a valid digital address (e.g. AK-039-5028)."
        )


GHANA_REGIONS = [
    ("ahafo", "Ahafo"),
    ("ashanti", "Ashanti"),
    ("bono", "Bono"),
    ("bono_east", "Bono East"),
    ("central", "Central"),
    ("eastern", "Eastern"),
    ("greater_accra", "Greater Accra"),
    ("north_east", "North East"),
    ("northern", "Northern"),
    ("oti", "Oti"),
    ("savannah", "Savannah"),
    ("upper_east", "Upper East"),
    ("upper_west", "Upper West"),
    ("volta", "Volta"),
    ("western", "Western"),
    ("western_north", "Western North"),
]

GHANA_PHONE_PREFIXES = {
    "024": "MTN",
    "025": "MTN",
    "053": "MTN",
    "054": "MTN",
    "055": "MTN",
    "059": "MTN",
    "020": "Telecel",
    "050": "Telecel",
    "026": "AirtelTigo",
    "056": "AirtelTigo",
    "027": "AirtelTigo",
    "057": "AirtelTigo",
}


def detect_carrier(phone):
    """Return the carrier name for a Ghana phone number, or None."""
    cleaned = re.sub(r"[\s\-()]", "", phone)
    if cleaned.startswith("+233"):
        cleaned = "0" + cleaned[4:]
    if cleaned.startswith("233"):
        cleaned = "0" + cleaned[3:]
    prefix = cleaned[:3]
    return GHANA_PHONE_PREFIXES.get(prefix)
