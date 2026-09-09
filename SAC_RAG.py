import os
from pypdf import PdfReader


# ============================================================
# CONFIGURATION
# ============================================================

PDF_PATH = os.path.join(
    "knowledge_base",
    "SAC Standards.pdf"
)


# ============================================================
# EXTRACT PDF TEXT
# ============================================================

def extract_pdf_text(pdf_path):

    reader = PdfReader(pdf_path)

    print(f"PDF loaded successfully.")
    print(f"Total pages: {len(reader.pages)}")

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text()

        if text:
            text = text.strip()
        else:
            text = ""

        pages.append({
            "page_number": page_number,
            "text": text
        })

        print(
            f"Page {page_number}: "
            f"{len(text)} characters extracted"
        )

    return pages


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("============================================")
    print("SAC STANDARDS PDF INGESTION")
    print("============================================")

    pages = extract_pdf_text(PDF_PATH)

    print()
    print("============================================")
    print("EXTRACTION COMPLETED")
    print("============================================")

    total_characters = sum(
        len(page["text"])
        for page in pages
    )

    print(f"Pages extracted: {len(pages)}")
    print(f"Total characters: {total_characters}")

    print()
    print("============================================")
    print("FIRST PAGE PREVIEW")
    print("============================================")

    print(pages[0]["text"][:3000])
