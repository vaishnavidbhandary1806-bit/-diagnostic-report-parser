import pdfplumber
import sys
import os

def extract_raw_text(pdf_path: str) -> str:
    all_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or "[NO TEXT FOUND ON THIS PAGE]"
            all_text.append(f"\n----- PAGE {i} -----\n{text}")
    return "\n".join(all_text)


def extract_with_layout(pdf_path: str) -> str:
    all_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text(layout=True) or "[NO TEXT FOUND ON THIS PAGE]"
            all_text.append(f"\n----- PAGE {i} (layout mode) -----\n{text}")
    return "\n".join(all_text)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_raw_text.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        sys.exit(1)

    print("=" * 60)
    print("DEFAULT EXTRACTION")
    print("=" * 60)
    print(extract_raw_text(pdf_path))

    print("\n\n")
    print("=" * 60)
    print("LAYOUT-PRESERVED EXTRACTION")
    print("=" * 60)
    print(extract_with_layout(pdf_path))