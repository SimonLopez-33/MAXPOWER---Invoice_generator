
"""
Invoice monetary calculations.
"""

from decimal import Decimal, ROUND_HALF_UP

from .config import HOURLY_RATE, HST_RATE
from .models import Shift


CENT = Decimal("0.01")


def round_currency(value: Decimal) -> Decimal:
    """
    Round a monetary value to the nearest cent.
    """

    return value.quantize(
        CENT,
        rounding=ROUND_HALF_UP,
    )


def calculate_shift_amount(shift: Shift) -> Decimal:
    """
    Calculate gross amount earned for one shift.
    """

    return round_currency(
        shift.hours * HOURLY_RATE
    )


def calculate_subtotal(shifts: list[Shift]) -> Decimal:
    """
    Calculate the subtotal for all invoice shifts.
    """

    return round_currency(
        sum(
            (calculate_shift_amount(shift) for shift in shifts),
            start=Decimal("0.00"),
        )
    )


def calculate_hst(subtotal: Decimal) -> Decimal:
    """
    Calculate HST.

    For the current contract configuration, HST_RATE is 0.00.
    """

    return round_currency(
        subtotal * HST_RATE
    )


def calculate_total(
    subtotal: Decimal,
    hst: Decimal,
) -> Decimal:
    """
    Calculate final invoice total.
    """

    return round_currency(
        subtotal + hst
    )


def format_currency(value: Decimal) -> str:
    """
    Format a Decimal for the PDF form.

    Example:
        Decimal("125.5") -> "125.50"
    """

    return f"{value:.2f}"