"""
Domain models used by the invoice generator.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Shift:
    """
    Represents one worked shift.

    Attributes:
        date:
            Calendar date on which the shift was worked.

        shift_type:
            Human-readable shift category, such as Morning or Evening.

        hours:
            Number of hours worked during the shift.
    """

    date: date
    shift_type: str
    hours: Decimal


@dataclass(frozen=True)
class InvoicePeriod:
    """
    Represents one biweekly invoice/payroll period.
    """

    start_date: date
    end_date: date
    pay_date: date