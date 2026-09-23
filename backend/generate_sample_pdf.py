import pymupdf as fitz
from app.services.demo_data import SAMPLE_RESUME

def create_pdf():
    doc = fitz.open()
    page = doc.new_page(width=595, height=842) # A4
    rect = fitz.Rect(50, 50, 545, 792)
    page.insert_textbox(rect, SAMPLE_RESUME, fontsize=10, fontname="helv", color=(0.1, 0.1, 0.1))
    doc.save("backend/data/sample_resume.pdf")
    doc.close()
    print("Generated backend/data/sample_resume.pdf")

if __name__ == "__main__":
    create_pdf()
