"""
Application-wide configuration.

Values in this file are expected to change rarely. Variable invoice data,
such as individual shifts and hours worked, belongs in data/invoice.json.
"""

from decimal import Decimal
from pathlib import Path


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TEMPLATE_PATH = PROJECT_ROOT / "templates" / "MaxPower_Vendor_Package.pdf"
INPUT_PATH = PROJECT_ROOT / "data" / "invoice.json"
OUTPUT_DIRECTORY = PROJECT_ROOT / "output"


# ---------------------------------------------------------------------------
# Contractor information
# ---------------------------------------------------------------------------

CONTRACTOR_NAME = "YOUR NAME"

SERVICE_LOCATION = "YOUR SERVICE LOCATION"

HOURLY_RATE = Decimal("00.00")


# ---------------------------------------------------------------------------
# Payroll schedule
# ---------------------------------------------------------------------------

# Known payroll cycle used as the reference point for all future periods.
#
# Period:
#   2026-08-01 through 2026-08-14
#
# Pay date:
#   2026-08-21
#
# Every subsequent period begins 14 days after the previous period.
REFERENCE_PERIOD_START = "2026-08-01"
REFERENCE_PAY_DATE = "2026-08-21"


# ---------------------------------------------------------------------------
# Invoice rules
# ---------------------------------------------------------------------------

HST_RATE = Decimal("0.00")

VALID_SHIFT_TYPES = {
    "Morning",
    "Evening",
    "Night",
}

MAX_INVOICE_ROWS = 7