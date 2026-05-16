from datetime import datetime, timezone
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
import math


def generate_certificate_pdf(
    *,
    user_name: str,
    internship_title: str,
    duration_weeks: int,
    skills_acquired: list[str],
    certificate_id: str,
    organization_name: str = "Acme Global Technologies",
    director_name: str = "Alice Vance",
    mentor_name: str = "Robert Chen",
    output_dir: str | Path,
) -> Path:

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    certificate_path = output_path / f"{certificate_id}_detailed.pdf"

    doc = canvas.Canvas(str(certificate_path), pagesize=landscape(A4))
    width, height = landscape(A4)

    # 1. Background Watermark (Rotated and Transparent)
    doc.saveState()
    doc.setFillColor(colors.Color(0.9, 0.9, 0.95, alpha=0.3))  # Very light grey-blue
    doc.setFont("Helvetica-Bold", 120)
    doc.translate(width / 2, height / 2)
    doc.rotate(30)
    doc.drawCentredString(0, -40, organization_name.upper())
    doc.restoreState()

    # 2. Triple Border for an Ornate Look
    doc.setStrokeColor(colors.HexColor("#0A2540"))
    doc.setLineWidth(4)
    doc.rect(20, 20, width - 40, height - 40)
    doc.setStrokeColor(colors.HexColor("#C4A25C"))  # Gold inner border
    doc.setLineWidth(2)
    doc.rect(26, 26, width - 52, height - 52)
    doc.setStrokeColor(colors.HexColor("#0A2540"))
    doc.setLineWidth(1)
    doc.rect(30, 30, width - 60, height - 60)

    # 3. Header & Title
    doc.setFillColor(colors.HexColor("#0A2540"))
    doc.setFont("Helvetica-Bold", 16)
    doc.drawCentredString(width / 2, height - 80, organization_name.upper())

    doc.setFont("Times-Bold", 40)
    doc.setFillColor(colors.HexColor("#C4A25C"))  # Gold Title
    doc.drawCentredString(width / 2, height - 130, "CERTIFICATE OF EXCELLENCE")

    # 4. Detailed Body Text
    doc.setFillColor(colors.black)
    doc.setFont("Helvetica", 14)
    doc.drawCentredString(
        width / 2,
        height - 180,
        "This detailed record of achievement is hereby granted to",
    )

    # User Name
    doc.setFont("Times-BoldItalic", 34)
    doc.setFillColor(colors.HexColor("#0A2540"))
    doc.drawCentredString(width / 2, height - 230, user_name)

    # Core Detail Paragraph
    doc.setFillColor(colors.black)
    doc.setFont("Helvetica", 12)
    text_y = height - 270
    doc.drawCentredString(
        width / 2,
        text_y,
        f"for the meticulous and successful completion of the {internship_title} program.",
    )
    doc.drawCentredString(
        width / 2,
        text_y - 20,
        f"Spanning {duration_weeks} weeks of rigorous training and practical application,",
    )
    doc.drawCentredString(
        width / 2,
        text_y - 40,
        "the candidate has demonstrated exceptional proficiency in the following domains:",
    )

    # 5. Dynamic Skills List
    doc.setFont("Helvetica-Bold", 12)
    skills_start_y = text_y - 75
    # Center the list block by calculating a rough offset
    list_x = width / 2 - 150
    for i, skill in enumerate(skills_acquired[:4]):  # Limit to 4 skills for space
        doc.drawString(list_x, skills_start_y - (i * 20), f"• {skill}")

    # 6. Verification Details (Bottom Left)
    footer_y = 100
    doc.setFont("Helvetica", 10)
    doc.drawString(80, footer_y + 30, f"Certificate ID: {certificate_id}")
    doc.drawString(
        80,
        footer_y + 15,
        f"Date of Issue: {datetime.now(timezone.utc).strftime('%B %d, %Y')}",
    )
    doc.drawString(80, footer_y, "Status: VERIFIED & OFFICIAL")

    # 7. Official Gold Seal (Bottom Center)
    seal_x = width / 2
    seal_y = footer_y + 15
    doc.setFillColor(colors.HexColor("#C4A25C"))
    doc.setStrokeColor(colors.HexColor("#A38340"))
    doc.setLineWidth(2)
    # Draw a simple sunburst/seal base
    for angle in range(0, 360, 15):
        rad = math.radians(angle)
        end_x = seal_x + 40 * math.cos(rad)
        end_y = seal_y + 40 * math.sin(rad)
        doc.line(seal_x, seal_y, end_x, end_y)
    # Inner circles for the seal
    doc.circle(seal_x, seal_y, 32, fill=1, stroke=1)
    doc.setFillColor(colors.white)
    doc.circle(seal_x, seal_y, 28, fill=1, stroke=0)
    doc.setFillColor(colors.HexColor("#0A2540"))
    doc.setFont("Times-Bold", 10)
    doc.drawCentredString(seal_x, seal_y + 2, "OFFICIAL")
    doc.drawCentredString(seal_x, seal_y - 10, "SEAL")

    # 8. Dual Signatures (Bottom Right)
    # Signature 1: Mentor
    sig1_x = width - 380
    doc.setStrokeColor(colors.black)
    doc.setLineWidth(1)
    doc.line(sig1_x, footer_y, sig1_x + 120, footer_y)
    doc.setFont("Helvetica-Bold", 11)
    doc.drawCentredString(sig1_x + 60, footer_y - 15, mentor_name)
    doc.setFont("Helvetica", 9)
    doc.drawCentredString(sig1_x + 60, footer_y - 28, "Directing Mentor")

    # Signature 2: Director
    sig2_x = width - 200
    doc.line(sig2_x, footer_y, sig2_x + 120, footer_y)
    doc.setFont("Helvetica-Bold", 11)
    doc.drawCentredString(sig2_x + 60, footer_y - 15, director_name)
    doc.setFont("Helvetica", 9)
    doc.drawCentredString(sig2_x + 60, footer_y - 28, "Managing Director")

    doc.save()
    return certificate_path


# Example Usage:
# generate_highly_detailed_certificate(
#     user_name="Jane Doe",
#     internship_title="Advanced Cloud Architecture",
#     duration_weeks=24,
#     skills_acquired=[
#         "Microservices Design & Implementation",
#         "Kubernetes Cluster Management",
#         "AWS Security Protocols",
#         "CI/CD Pipeline Automation"
#     ],
#     certificate_id="CERT-2026-992",
#     output_dir="./certificates"
# )
