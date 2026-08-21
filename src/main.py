"""
Application entry point for the MaxPower invoice generator.

Workflow:
    1. Read invoice.json.
    2. Validate each shift.
    3. Determine the appropriate payroll period.
    4. Verify all shifts belong to that period.
    5. Calculate invoice values.
    6. Fill the existing PDF form.
    7. Save the generated invoice.
"""

import json
from decimal import Decimal, InvalidOperation

from .config import (
    INPUT_PATH,
    VALID_SHIFT_TYPES,
)
from .dates import (
    get_invoice_period_for_shift,
    parse_date,
)
from .models import Shift
from .pdf_writer import generate_invoice


def load_shift_data() -> list[Shift]:
    """
    Read and validate shifts from invoice.json.
    """

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    with INPUT_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    raw_shifts = data.get("shifts")

    if not isinstance(raw_shifts, list):
        raise ValueError(
            "'shifts' must be a JSON list."
        )

    if not raw_shifts:
        raise ValueError(
            "At least one shift must be provided."
        )

    shifts: list[Shift] = []

    for index, item in enumerate(
        raw_shifts,
        start=1,
    ):
        try:
            shift_date = parse_date(item["date"])
            shift_type = item["shift"]
            hours = Decimal(str(item["hours"]))

        except KeyError as error:
            raise ValueError(
                f"Shift {index} is missing required field: "
                f"{error.args[0]}"
            ) from error

        except ValueError as error:
            raise ValueError(
                f"Shift {index} contains an invalid date."
            ) from error

        except InvalidOperation as error:
            raise ValueError(
                f"Shift {index} contains invalid hours."
            ) from error

        if shift_type not in VALID_SHIFT_TYPES:
            valid_values = ", ".join(
                sorted(VALID_SHIFT_TYPES)
            )

            raise ValueError(
                f"Shift {index} has invalid shift type "
                f"'{shift_type}'. Valid values: {valid_values}."
            )

        if hours <= 0:
            raise ValueError(
                f"Shift {index} must contain more than 0 hours."
            )

        shifts.append(
            Shift(
                date=shift_date,
                shift_type=shift_type,
                hours=hours,
            )
        )

    return shifts


def validate_single_pay_period(
    shifts: list[Shift],
):
    """
    Confirm that all supplied shifts belong to one payroll period.

    Mixing periods could cause an incorrect invoice, so the program
    fails rather than silently discarding or moving shifts.
    """

    expected_period = get_invoice_period_for_shift(
        shifts[0].date
    )

    for shift in shifts:
        current_period = get_invoice_period_for_shift(
            shift.date
        )

        if current_period != expected_period:
            raise ValueError(
                "All shifts must belong to the same invoice period. "
                f"{shift.date.isoformat()} belongs to "
                f"{current_period.start_date.isoformat()} through "
                f"{current_period.end_date.isoformat()}."
            )

    return expected_period


def main() -> None:
    """
    Run the invoice-generation workflow.
    """

    print()
    print("MaxPower Invoice Generator")
    print("=" * 40)

    try:
        shifts = load_shift_data()

        period = validate_single_pay_period(
            shifts
        )

        print(
            "Invoice period:",
            period.start_date,
            "to",
            period.end_date,
        )

        print(
            "Pay date:",
            period.pay_date,
        )

        print(
            "Shifts:",
            len(shifts),
        )

        output_path = generate_invoice(
            shifts,
            period,
        )

    except (
        FileNotFoundError,
        ValueError,
        json.JSONDecodeError,
    ) as error:
        print()
        print(f"ERROR: {error}")
        print()
        print("Invoice was not generated.")
        return

    print()
    print("Invoice generated successfully.")
    print(f"Output: {output_path}")
    print()
    print(
        "IMPORTANT: Review the invoice and add your "
        "signature before submitting it."
    )


if __name__ == "__main__":
    main()