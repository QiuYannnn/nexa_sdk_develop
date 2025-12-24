#!/usr/bin/env python3
"""
Combine all Markdown files in the current directory into one file.
"""
import os
import glob
from datetime import datetime

def combine_markdown():
    # Get all markdown files in current directory
    md_files = sorted(glob.glob("*.md") + glob.glob("*.markdown"))

    if not md_files:
        print("No Markdown files found in current directory.")
        return

    print(f"Found {len(md_files)} Markdown files:")
    for f in md_files:
        print(f"  - {f}")

    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"combined_{timestamp}.md"

    # Combine files
    combined_content = []
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Add file header and content
            combined_content.append(f"\n\n---\n\n# {md_file}\n\n")
            combined_content.append(content)

        except Exception as e:
            print(f"Error reading {md_file}: {e}")

    # Write combined file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(combined_content))

    print(f"\nCombined into: {output_file}")
    print(f"Total size: {os.path.getsize(output_file):,} bytes")

if __name__ == "__main__":
    combine_markdown()
