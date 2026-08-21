"""
Date and payroll-period calculations.
"""

from datetime import date, timedelta

from .config import REFERENCE_PAY_DATE, REFERENCE_PERIOD_START
from .models import InvoicePeriod


PAY_PERIOD_LENGTH_DAYS = 14
PAYMENT_DELAY_DAYS = 7


def parse_date(value: str) -> date:
    """
    Convert an ISO-formatted date string into a date object.

    Expected format:
        YYYY-MM-DD
    """

    return date.fromisoformat(value)


def get_invoice_period_for_shift(shift_date: date) -> InvoicePeriod:
    """
    Determine the payroll period containing a given shift date.

    The payroll schedule repeats every 14 days beginning from the configured
    reference period.

    Args:
        shift_date:
            Date of a worked shift.

    Returns:
        InvoicePeriod containing the appropriate start date, end date,
        and pay date.
    """

    reference_start = parse_date(REFERENCE_PERIOD_START)
    reference_pay_date = parse_date(REFERENCE_PAY_DATE)

    days_from_reference = (shift_date - reference_start).days

    period_index = days_from_reference // PAY_PERIOD_LENGTH_DAYS

    period_start = (
        reference_start
        + timedelta(days=period_index * PAY_PERIOD_LENGTH_DAYS)
    )

    period_end = period_start + timedelta(
        days=PAY_PERIOD_LENGTH_DAYS - 1
    )

    pay_date = (
        reference_pay_date
        + timedelta(days=period_index * PAY_PERIOD_LENGTH_DAYS)
    )

    return InvoicePeriod(
        start_date=period_start,
        end_date=period_end,
        pay_date=pay_date,
    )


def ordinal(day: int) -> str:
    """
    Convert a day number into an English ordinal.

    Examples:
        1  -> 1st
        2  -> 2nd
        3  -> 3rd
        4  -> 4th
        11 -> 11th
        21 -> 21st
    """

    if 10 <= day % 100 <= 20:
        suffix = "th"
    else:
        suffix = {
            1: "st",
            2: "nd",
            3: "rd",
        }.get(day % 10, "th")

    return f"{day}{suffix}"


def build_shift_description(
    shift_date: date,
    shift_type: str,
) -> str:
    """
    Build the description used in the invoice line item.

    Example:
        Sunday Aug 2nd Evening Shift
    """

    weekday = shift_date.strftime("%A")
    month = shift_date.strftime("%b")
    day = ordinal(shift_date.day)

    return f"{weekday} {month} {day} {shift_type} Shift"