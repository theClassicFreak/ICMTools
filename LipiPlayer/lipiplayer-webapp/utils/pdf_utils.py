import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf(transcription_data, file_name, root_note, total_length):
    """Generate a PDF report from transcription data and return as BytesIO."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Courier", 12)
    c.drawString(50, 750, "Transcription Report")
    c.drawString(50, 735, f"File: {file_name}")
    c.drawString(50, 720, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(50, 705, f"Root Note: {root_note}")
    c.drawString(50, 690, f"Total Duration: {total_length}")
    c.drawString(50, 675, "-" * 80)
    y = 660
    c.drawString(50, y, "Timestamp")
    c.drawString(150, y, "Frequency")
    c.drawString(250, y, "Solfege")
    c.drawString(350, y, "Duration")
    c.drawString(450, y, "Count")
    y -= 20
    for row in transcription_data:
        if y < 50:
            c.showPage()
            c.setFont("Courier", 12)
            y = 750
        c.drawString(50, y, str(row[0]))
        c.drawString(150, y, str(row[1]))
        c.drawString(250, y, str(row[2]))
        c.drawString(350, y, str(row[3]))
        c.drawString(450, y, str(row[4]))
        y -= 20
    c.drawString(50, y, "-" * 80)
    y -= 20
    c.drawString(50, y, f"Total Notes: {len(transcription_data)}")
    y -= 20
    try:
        total_duration = sum(float(str(row[3]).replace("s", "")) for row in transcription_data)
    except Exception:
        total_duration = 0.0
    c.drawString(50, y, f"Total Duration of Notes: {total_duration:.3f} seconds")
    c.save()
    buffer.seek(0)
    return buffer