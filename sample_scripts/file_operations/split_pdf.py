#!/usr/bin/env python3
"""
Split a PDF file into individual pages.
Requires: pip install PyPDF2
Usage: python split_pdf.py <input.pdf>
"""
import os
import sys

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    print("PyPDF2 is required. Install with: pip install PyPDF2")
    exit(1)

def split_pdf(input_file):
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return

    base_name = os.path.splitext(input_file)[0]

    reader = PdfReader(input_file)
    num_pages = len(reader.pages)

    print(f"Splitting {input_file} ({num_pages} pages)")

    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)

        output_file = f"{base_name}_page_{i+1:03d}.pdf"
        with open(output_file, 'wb') as f:
            writer.write(f)

        print(f"Created: {output_file}")

    print(f"\nSplit into {num_pages} files")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # If no argument, try to find first PDF in current directory
        import glob
        pdfs = glob.glob("*.pdf")
        if pdfs:
            print(f"No file specified, using: {pdfs[0]}")
            split_pdf(pdfs[0])
        else:
            print("Usage: python split_pdf.py <input.pdf>")
    else:
        split_pdf(sys.argv[1])
