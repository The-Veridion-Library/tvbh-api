# app/pdf_utils.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from io import BytesIO
import qrcode

def generate_label_pdf(book, paper_id: str, base_url: str) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 740, "TVBH Book Label")

    c.setFont("Helvetica", 12)
    c.drawString(50, 710, f"Title: {book.title}")
    c.drawString(50, 690, f"Author: {book.author}")
    c.drawString(50, 670, f"ISBN: {book.isbn or 'N/A'}")
    c.drawString(50, 650, f"Book ID: {book.id}")
    c.drawString(50, 630, f"Paper ID: {paper_id}")

    # QR Code → verification page
    qr = qrcode.make(f"{base_url}/label/verify/{paper_id}")
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    qr_image = ImageReader(qr_buffer)
    c.drawImage(qr_image, 400, 620, width=150, height=150)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer