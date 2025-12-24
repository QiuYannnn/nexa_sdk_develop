#!/usr/bin/env python3
"""
Clean text files for TTS (Text-to-Speech) engines.
Removes URLs, special characters, and normalizes text.
"""
import os
import re
import glob
from datetime import datetime

def clean_for_tts(text):
    """Clean text for TTS engines"""
    result = text

    # Replace smart quotes and dashes
    replacements = {
        '"': '"', '"': '"', ''': "'", ''': "'",
        '…': '...', '—': ' - ', '–': ' - ',
        '•': '-', '→': 'to', '←': 'from',
        '©': 'copyright', '®': 'registered', '™': 'trademark',
        '°': ' degrees', '±': 'plus or minus',
        '×': 'times', '÷': 'divided by',
    }

    for old, new in replacements.items():
        result = result.replace(old, new)

    # Remove URLs
    result = re.sub(r'https?://\S+', '', result)
    result = re.sub(r'www\.\S+', '', result)

    # Remove email addresses
    result = re.sub(r'\S+@\S+\.\S+', '', result)

    # Remove markdown formatting
    result = re.sub(r'\*\*(.+?)\*\*', r'\1', result)
    result = re.sub(r'\*(.+?)\*', r'\1', result)
    result = re.sub(r'`(.+?)`', r'\1', result)
    result = re.sub(r'^#+\s*', '', result, flags=re.MULTILINE)
    result = re.sub(r'^\s*[-*]\s+', '', result, flags=re.MULTILINE)
    result = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', result)

    # Remove code blocks
    result = re.sub(r'```[\s\S]*?```', '', result)

    # Normalize whitespace
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'\n\s*\n', '\n\n', result)

    return result.strip()

def process_files():
    # Get text and markdown files
    files = glob.glob("*.txt") + glob.glob("*.md")

    if not files:
        print("No .txt or .md files found in current directory.")
        return

    print(f"Found {len(files)} files to process")

    for input_file in files:
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()

            cleaned = clean_for_tts(content)

            output_file = f"tts_ready_{input_file}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(cleaned)

            print(f"Cleaned: {input_file} -> {output_file}")

        except Exception as e:
            print(f"Error processing {input_file}: {e}")

    print("\nDone!")

if __name__ == "__main__":
    process_files()
