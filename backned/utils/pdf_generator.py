from datetime import datetime, timezone
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_certificate_pdf(
    *,
    user_name: str,
    internship_title: str,
    duration_weeks: int,
    certificate_id: str,
    output_dir: str | Path,
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    certificate_path = output_path / f"{certificate_id}.pdf"
    doc = canvas.Canvas(str(certificate_path), pagesize=A4)
    width, height = A4

    border_margin = 24
    doc.setStrokeColor(colors.HexColor("#0F3D5E"))
    doc.setLineWidth(2)
    doc.rect(border_margin, border_margin, width - (2 * border_margin), height - (2 * border_margin))

    doc.setFillColor(colors.HexColor("#0F3D5E"))
    doc.setFont("Helvetica-Bold", 30)
    doc.drawCentredString(width / 2, height - 120, "Certificate of Completion")

    doc.setFillColor(colors.black)
    doc.setFont("Helvetica", 14)
    doc.drawCentredString(width / 2, height - 185, "This is to certify that")

    doc.setFont("Helvetica-Bold", 26)
    doc.drawCentredString(width / 2, height - 235, user_name)

    doc.setFont("Helvetica", 13)
    doc.drawCentredString(width / 2, height - 285, "has successfully completed the internship")

    doc.setFont("Helvetica-Bold", 18)
    doc.drawCentredString(width / 2, height - 320, internship_title)

    doc.setFont("Helvetica", 13)
    doc.drawCentredString(
        width / 2,
        height - 355,
        f"Duration: {duration_weeks} week{'s' if duration_weeks != 1 else ''}",
    )

    doc.setFont("Helvetica", 12)
    doc.drawString(72, 140, f"Certificate ID: {certificate_id}")
    doc.drawString(72, 120, f"Issued on: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")

    doc.line(width - 230, 120, width - 72, 120)
    doc.drawString(width - 205, 102, "Authorized Signatory")

    doc.save()
    return certificate_path
