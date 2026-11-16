from dataclasses import dataclass
import fitz

@dataclass
class PageText:
    page: int
    text: str

def extract_pdf(data: bytes) -> list[PageText]:
    try:
        doc = fitz.open(stream=data, filetype="pdf")
    except Exception as exc:
        raise ValueError("This file is not a valid PDF.") from exc
    if doc.needs_pass:
        raise ValueError("This PDF is encrypted or password protected.")
    pages = [PageText(page=i + 1, text=page.get_text("text").strip()) for i, page in enumerate(doc)]
    doc.close()
    if not pages:
        raise ValueError("This PDF contains no pages.")
    if not any(p.text for p in pages):
        raise ValueError("No selectable text was found. This may be a scanned PDF; OCR support can be added later.")
    return pages
