"""
pdf_utils.py
Narzędzia do generowania i scalania plików PDF.
Brak zależności od Streamlit.
"""

import io

import numpy as np
from PIL import Image
from pypdf import PdfReader, PdfWriter


def image_to_pdf_bytes(image_array: np.ndarray) -> bytes:
    """Konwertuje tablicę numpy (obraz) do bajtów PDF w rozdzielczości 300 DPI."""
    image = Image.fromarray(image_array)
    if image.mode != "RGB":
        image = image.convert("RGB")
    output = io.BytesIO()
    image.save(output, format="PDF", resolution=300.0)
    return output.getvalue()


def merge_pdfs(pdf_files: list) -> bytes:
    """
    Scala listę plików PDF w jeden dokument.

    Parametry:
        pdf_files: lista obiektów z metodą .read() (UploadedFile Streamlit)
                   lub obiektów bytes.

    Zwraca bajty scalonego PDF.
    """
    writer = PdfWriter()
    for f in pdf_files:
        data = f.read() if hasattr(f, "read") else f
        reader = PdfReader(io.BytesIO(data))
        for page in reader.pages:
            writer.add_page(page)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()
