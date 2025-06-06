import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

def generate_pdf(transcription_data, file_name, root_note, total_length):
    """Generate a professional, more spacious and mobile-friendly PDF report."""
    buffer = io.BytesIO()
    # Use landscape for more width (optional, comment out if you want portrait)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=18
    )
    elements = []
    styles = getSampleStyleSheet()
    # Larger font for mobile readability
    title_style = ParagraphStyle('title', parent=styles['Title'], fontSize=22, spaceAfter=16)
    normal_style = ParagraphStyle('normal', parent=styles['Normal'], fontSize=13, spaceAfter=10)

    # Title and metadata
    title = Paragraph("<b>Transcription Report</b>", title_style)
    file_info = Paragraph(
        f"<b>File:</b> {file_name}<br/><b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
        f"<b>Root Note:</b> {root_note}<br/><b>Total Duration:</b> {total_length}",
        normal_style
    )
    elements.extend([title, file_info, Spacer(1, 18)])

    # Table data
    table_data = [["Timestamp", "Frequency", "Swara", "Duration", "Count"]]
    for row in transcription_data:
        table_data.append([str(col) for col in row])

    # Set column widths (adjust as needed)
    col_widths = [90, 80, 60, 80, 60]

    # Table style
    table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f5f5f5")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#333333")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 13),
        ('FONTSIZE', (0,1), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,1), (-1,-1), 8),
        ('TOPPADDING', (0,1), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.7, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f9f9f9")]),
    ])

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(table_style)
    elements.append(table)

    # Summary
    elements.append(Spacer(1, 18))
    total_notes = len(transcription_data)
    try:
        total_note_duration = sum(float(str(row[3]).replace("s", "")) for row in transcription_data)
    except Exception:
        total_note_duration = 0.0
    summary = Paragraph(
        f"<b>Total Notes:</b> {total_notes}<br/><b>Total Duration of Notes:</b> {total_note_duration:.3f} seconds",
        normal_style
    )
    elements.append(summary)

    doc.build(elements)
    buffer.seek(0)
    return buffer