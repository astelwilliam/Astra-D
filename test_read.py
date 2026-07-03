# test_read.py

import pdf_utils

text = pdf_utils.read_pdf(
    r"C:\Users\astel\Downloads\Paper-3.1-BUSINESS-ETHICS-CORPORATE-GOVERNANCE.pdf"
)

print(text[:3000])
print("\nLength:", len(text))