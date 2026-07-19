from pypdf import PdfReader

pdf = r"C:\Users\astel\Downloads\Paper-3.1-BUSINESS-ETHICS-CORPORATE-GOVERNANCE.pdf"

reader = PdfReader(pdf)

print("Pages:", len(reader.pages))

for i, page in enumerate(reader.pages[:3]):
    text = page.extract_text()

    print(f"\nPAGE {i+1}")

    if text:
        print("Length:", len(text))
        print(repr(text[:200]))
    else:
        print("Length: 0")
        print("No text extracted")