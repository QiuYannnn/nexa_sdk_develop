#!/usr/bin/env python3
"""
Combine all PDF files in the current directory into one file.
Requires: pip install PyPDF2
"""
import os
import glob
from datetime import datetime

try:
    from PyPDF2 import PdfMerger
except ImportError:
    print("PyPDF2 is required. Install with: pip install PyPDF2")
    exit(1)

def combine_pdfs():
    # Get all PDF files in current directory
    pdf_files = sorted(glob.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in current directory.")
        return

    print(f"Found {len(pdf_files)} PDF files:")
    for f in pdf_files:
        print(f"  - {f}")

    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"combined_{timestamp}.pdf"

    # Combine PDFs
    merger = PdfMerger()

    for pdf_file in pdf_files:
        try:
            merger.append(pdf_file)
            print(f"Added: {pdf_file}")
        except Exception as e:
            print(f"Error adding {pdf_file}: {e}")

    # Write combined file
    merger.write(output_file)
    merger.close()

    print(f"\nCombined into: {output_file}")
    print(f"Total size: {os.path.getsize(output_file):,} bytes")

if __name__ == "__main__":
    combine_pdfs()
