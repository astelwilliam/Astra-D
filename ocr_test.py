from pdf2image import convert_from_path
import pytesseract

PDF_FILE = r"C:\Users\astel\Downloads\Paper-3.1-BUSINESS-ETHICS-CORPORATE-GOVERNANCE.pdf"

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

POPPLER_PATH = (
    r"C:\poppler\Release-26.02.0-0\poppler-26.02.0\Library\bin"
)

print("Converting PDF...")

images = convert_from_path(
    PDF_FILE,
    poppler_path=POPPLER_PATH,
    first_page=1,
    last_page=1,
)

print("Running OCR...")

text = pytesseract.image_to_string(images[0])

print(text[:3000])