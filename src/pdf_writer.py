"""
PDF form generation.

This module maps validated invoice data onto the existing fillable
MaxPower invoice PDF.
"""

from pathlib import Path

from pypdf import PdfReader, PdfWriter

from .calculations import (
    calculate_hst,
    calculate_shift_amount,
    calculate_subtotal,
    calculate_total,
    format_currency,
)
from .config import (
    CONTRACTOR_NAME,
    MAX_INVOICE_ROWS,
    OUTPUT_DIRECTORY,
    SERVICE_LOCATION,
    TEMPLATE_PATH,
)
from .dates import build_shift_description
from .models import InvoicePeriod, Shift


def format_pdf_date(value) -> str:
    """
    Format dates consistently for the invoice.
    """

    return value.isoformat()


def build_invoice_number(period: InvoicePeriod) -> str:
    """
    Build invoice number from the pay date.

    Example:
        INV-2026-09-04
    """

    return f"INV-{period.pay_date.isoformat()}"


def build_pdf_fields(
    shifts: list[Shift],
    period: InvoicePeriod,
) -> dict[str, str]:
    """
    Build the field-value mapping sent to the fillable PDF.
    """

    subtotal = calculate_subtotal(shifts)
    hst = calculate_hst(subtotal)
    total = calculate_total(subtotal, hst)

    fields: dict[str, str] = {
        "invoice_no": build_invoice_number(period),
        "invoice_date": format_pdf_date(period.pay_date),

        "service_location": SERVICE_LOCATION,

        "period_from": format_pdf_date(period.start_date),
        "period_to": format_pdf_date(period.end_date),

        "subtotal": format_currency(subtotal),
        "hst": format_currency(hst),
        "total": format_currency(total),

        "inv_cert_name": CONTRACTOR_NAME,
        "inv_cert_date": format_pdf_date(period.pay_date),

        # Signature intentionally remains blank.
        "inv_cert_signature": "",
    }

    for row_number, shift in enumerate(shifts, start=1):
        amount = calculate_shift_amount(shift)

        fields[f"qty_{row_number}"] = "1"
        fields[f"desc_{row_number}"] = build_shift_description(
            shift.date,
            shift.shift_type,
        )

        # Quantity is always 1, therefore the unit price represents
        # the complete value of the shift.
        fields[f"price_{row_number}"] = format_currency(amount)
        fields[f"amount_{row_number}"] = format_currency(amount)

    return fields


def generate_invoice(
    shifts: list[Shift],
    period: InvoicePeriod,
) -> Path:
    """
    Generate a completed invoice PDF.

    Returns:
        Path to the newly created invoice.
    """

    if len(shifts) > MAX_INVOICE_ROWS:
        raise ValueError(
            f"The PDF supports a maximum of {MAX_INVOICE_ROWS} "
            f"invoice rows, but {len(shifts)} shifts were provided."
        )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    reader = PdfReader(TEMPLATE_PATH)
    writer = PdfWriter()

    writer.append(reader)

    fields = build_pdf_fields(
        shifts,
        period,
    )

    # Invoice is located on page 2.
    invoice_page = writer.pages[1]

    writer.update_page_form_field_values(
        invoice_page,
        fields,
        auto_regenerate=True,
    )

    output_path = (
        OUTPUT_DIRECTORY
        / f"{build_invoice_number(period)}.pdf"
    )

    with output_path.open("wb") as output_file:
        writer.write(output_file)

    return output_path