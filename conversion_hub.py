#!/usr/bin/env python3
"""
Conversion & Data Cleaning Hub
A modular, expandable application for document conversion and data cleaning
Uses CustomTkinter for a modern dark-themed GUI
"""

import customtkinter as ctk
import os
import sys
import json
import re
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from datetime import datetime
from abc import ABC, abstractmethod
import html
import csv
from typing import List, Dict, Any, Optional
import tempfile
import shutil

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Optional imports - graceful degradation if not available
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    PDFKIT_AVAILABLE = False

try:
    from PyPDF2 import PdfReader, PdfMerger
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


# ============================================================================
# Converter Base Class and Registry
# ============================================================================

class ConverterBase(ABC):
    """Base class for all converters"""

    name: str = "Base Converter"
    description: str = "Base converter class"
    input_formats: List[str] = []
    output_formats: List[str] = []
    icon: str = "📄"

    @abstractmethod
    def convert(self, input_path: str, output_path: str, options: Dict = None) -> bool:
        """Perform the conversion"""
        pass

    def get_options_frame(self, parent) -> Optional[ctk.CTkFrame]:
        """Return a frame with converter-specific options. Override in subclasses."""
        return None


class CleanerBase(ABC):
    """Base class for all data cleaners"""

    name: str = "Base Cleaner"
    description: str = "Base cleaner class"
    supported_formats: List[str] = []
    icon: str = "🧹"

    @abstractmethod
    def clean(self, data: str, options: Dict = None) -> str:
        """Clean the data"""
        pass

    def get_options_frame(self, parent) -> Optional[ctk.CTkFrame]:
        """Return a frame with cleaner-specific options. Override in subclasses."""
        return None


class PluginRegistry:
    """Registry for converters and cleaners"""

    converters: List[ConverterBase] = []
    cleaners: List[CleanerBase] = []

    @classmethod
    def register_converter(cls, converter: ConverterBase):
        cls.converters.append(converter)

    @classmethod
    def register_cleaner(cls, cleaner: CleanerBase):
        cls.cleaners.append(cleaner)


# ============================================================================
# Built-in Converters
# ============================================================================

class MarkdownToHTMLConverter(ConverterBase):
    name = "Markdown → HTML"
    description = "Convert Markdown files to HTML with customizable styling"
    input_formats = [".md", ".markdown"]
    output_formats = [".html"]
    icon = "📝"

    def convert(self, input_path: str, output_path: str, options: Dict = None) -> bool:
        options = options or {}
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            if MARKDOWN_AVAILABLE:
                html_content = markdown.markdown(
                    md_content,
                    extensions=['tables', 'fenced_code', 'codehilite', 'toc']
                )
            else:
                # Basic fallback conversion
                html_content = self._basic_markdown_to_html(md_content)

            # Add styling
            if options.get('include_styles', True):
                html_content = self._wrap_with_styles(html_content, options.get('dark_mode', True))

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            return True
        except Exception as e:
            raise Exception(f"Markdown to HTML conversion failed: {str(e)}")

    def _basic_markdown_to_html(self, md: str) -> str:
        """Basic markdown to HTML without library"""
        lines = md.split('\n')
        html_lines = []
        in_code_block = False

        for line in lines:
            # Code blocks
            if line.startswith('```'):
                if in_code_block:
                    html_lines.append('</code></pre>')
                    in_code_block = False
                else:
                    html_lines.append('<pre><code>')
                    in_code_block = True
                continue

            if in_code_block:
                html_lines.append(html.escape(line))
                continue

            # Headers
            if line.startswith('######'):
                html_lines.append(f'<h6>{html.escape(line[6:].strip())}</h6>')
            elif line.startswith('#####'):
                html_lines.append(f'<h5>{html.escape(line[5:].strip())}</h5>')
            elif line.startswith('####'):
                html_lines.append(f'<h4>{html.escape(line[4:].strip())}</h4>')
            elif line.startswith('###'):
                html_lines.append(f'<h3>{html.escape(line[3:].strip())}</h3>')
            elif line.startswith('##'):
                html_lines.append(f'<h2>{html.escape(line[2:].strip())}</h2>')
            elif line.startswith('#'):
                html_lines.append(f'<h1>{html.escape(line[1:].strip())}</h1>')
            elif line.startswith('- ') or line.startswith('* '):
                html_lines.append(f'<li>{html.escape(line[2:])}</li>')
            elif line.strip():
                # Bold and italic
                processed = html.escape(line)
                processed = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', processed)
                processed = re.sub(r'\*(.+?)\*', r'<em>\1</em>', processed)
                processed = re.sub(r'`(.+?)`', r'<code>\1</code>', processed)
                html_lines.append(f'<p>{processed}</p>')
            else:
                html_lines.append('<br>')

        return '\n'.join(html_lines)

    def _wrap_with_styles(self, content: str, dark_mode: bool) -> str:
        """Wrap HTML content with styling"""
        if dark_mode:
            styles = """
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                   background: #1a1a2e; color: #eee; line-height: 1.6; padding: 2rem; max-width: 900px; margin: auto; }
            h1, h2, h3, h4, h5, h6 { color: #4fc3f7; margin-top: 1.5em; }
            code { background: #2d2d44; padding: 2px 6px; border-radius: 4px; font-family: 'Consolas', monospace; }
            pre { background: #2d2d44; padding: 1rem; border-radius: 8px; overflow-x: auto; }
            pre code { background: none; padding: 0; }
            a { color: #4fc3f7; }
            blockquote { border-left: 4px solid #4fc3f7; padding-left: 1rem; margin-left: 0; color: #aaa; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #444; padding: 8px; text-align: left; }
            th { background: #2d2d44; }
            """
        else:
            styles = """
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                   background: #fff; color: #333; line-height: 1.6; padding: 2rem; max-width: 900px; margin: auto; }
            h1, h2, h3, h4, h5, h6 { color: #2563eb; margin-top: 1.5em; }
            code { background: #f4f4f4; padding: 2px 6px; border-radius: 4px; font-family: 'Consolas', monospace; }
            pre { background: #f4f4f4; padding: 1rem; border-radius: 8px; overflow-x: auto; }
            pre code { background: none; padding: 0; }
            a { color: #2563eb; }
            blockquote { border-left: 4px solid #2563eb; padding-left: 1rem; margin-left: 0; color: #666; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background: #f4f4f4; }
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Converted Document</title>
    <style>{styles}</style>
</head>
<body>
{content}
</body>
</html>"""


class HTMLToMarkdownConverter(ConverterBase):
    name = "HTML → Markdown"
    description = "Convert HTML files to clean Markdown"
    input_formats = [".html", ".htm"]
    output_formats = [".md"]
    icon = "🔄"

    def convert(self, input_path: str, output_path: str, options: Dict = None) -> bool:
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            md_content = self._html_to_markdown(html_content)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)

            return True
        except Exception as e:
            raise Exception(f"HTML to Markdown conversion failed: {str(e)}")

    def _html_to_markdown(self, html_content: str) -> str:
        """Convert HTML to Markdown"""
        if BS4_AVAILABLE:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style elements
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()

            return self._process_element(soup.body if soup.body else soup)
        else:
            return self._basic_html_to_markdown(html_content)

    def _process_element(self, element) -> str:
        """Process BeautifulSoup element to Markdown"""
        if element is None:
            return ""

        result = []
        for child in element.children:
            if hasattr(child, 'name'):
                tag = child.name
                text = child.get_text().strip() if child.get_text() else ""

                if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    level = int(tag[1])
                    result.append(f"\n{'#' * level} {text}\n")
                elif tag == 'p':
                    inner = self._process_element(child)
                    result.append(f"\n{inner}\n")
                elif tag == 'a':
                    href = child.get('href', '')
                    result.append(f"[{text}]({href})")
                elif tag == 'strong' or tag == 'b':
                    result.append(f"**{text}**")
                elif tag == 'em' or tag == 'i':
                    result.append(f"*{text}*")
                elif tag == 'code':
                    result.append(f"`{text}`")
                elif tag == 'pre':
                    code = child.find('code')
                    code_text = code.get_text() if code else text
                    result.append(f"\n```\n{code_text}\n```\n")
                elif tag == 'ul' or tag == 'ol':
                    for i, li in enumerate(child.find_all('li', recursive=False)):
                        prefix = f"{i+1}." if tag == 'ol' else "-"
                        result.append(f"{prefix} {li.get_text().strip()}\n")
                elif tag == 'blockquote':
                    lines = text.split('\n')
                    result.append('\n' + '\n'.join(f"> {line}" for line in lines) + '\n')
                elif tag == 'br':
                    result.append('\n')
                elif tag == 'hr':
                    result.append('\n---\n')
                elif tag == 'img':
                    alt = child.get('alt', '')
                    src = child.get('src', '')
                    result.append(f"![{alt}]({src})")
                elif tag in ['div', 'section', 'article', 'main']:
                    result.append(self._process_element(child))
                else:
                    if text:
                        result.append(text)
            elif hasattr(child, 'string') and child.string:
                text = child.string.strip()
                if text:
                    result.append(text)

        return ' '.join(result)

    def _basic_html_to_markdown(self, html_content: str) -> str:
        """Basic HTML to Markdown without BeautifulSoup"""
        # Remove script and style
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

        # Convert headers
        for i in range(6, 0, -1):
            html_content = re.sub(rf'<h{i}[^>]*>(.*?)</h{i}>', rf'\n{"#" * i} \1\n', html_content, flags=re.IGNORECASE)

        # Convert other elements
        html_content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', r'[\2](\1)', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<hr\s*/?>', '\n---\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<p[^>]*>(.*?)</p>', r'\n\1\n', html_content, flags=re.IGNORECASE | re.DOTALL)

        # Remove remaining tags
        html_content = re.sub(r'<[^>]+>', '', html_content)

        # Clean up whitespace
        html_content = re.sub(r'\n\s*\n', '\n\n', html_content)
        html_content = html.unescape(html_content)

        return html_content.strip()


class HTMLToExcelConverter(ConverterBase):
    name = "HTML Tables → Excel"
    description = "Extract tables from HTML and convert to Excel spreadsheet"
    input_formats = [".html", ".htm"]
    output_formats = [".xlsx"]
    icon = "📊"

    def convert(self, input_path: str, output_path: str, options: Dict = None) -> bool:
        if not PANDAS_AVAILABLE:
            raise Exception("pandas is required for HTML to Excel conversion. Install with: pip install pandas openpyxl")

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            tables = pd.read_html(html_content)

            if not tables:
                raise Exception("No tables found in HTML file")

            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for i, table in enumerate(tables):
                    sheet_name = f'Table_{i+1}'
                    table.to_excel(writer, sheet_name=sheet_name, index=False)

            return True
        except Exception as e:
            raise Exception(f"HTML to Excel conversion failed: {str(e)}")


class PDFToTextConverter(ConverterBase):
    name = "PDF → Text"
    description = "Extract text content from PDF files"
    input_formats = [".pdf"]
    output_formats = [".txt"]
    icon = "📄"

    def convert(self, input_path: str, output_path: str, options: Dict = None) -> bool:
        if not PYPDF2_AVAILABLE:
            raise Exception("PyPDF2 is required for PDF conversion. Install with: pip install PyPDF2")

        try:
            reader = PdfReader(input_path)
            text_content = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n\n--- Page Break ---\n\n'.join(text_content))

            return True
        except Exception as e:
            raise Exception(f"PDF to Text conversion failed: {str(e)}")


class PDFMergeConverter(ConverterBase):
    name = "Merge PDFs"
    description = "Combine multiple PDF files into one"
    input_formats = [".pdf"]
    output_formats = [".pdf"]
    icon = "📑"

    def convert(self, input_path: str, output_path: str, options: Dict = None) -> bool:
        if not PYPDF2_AVAILABLE:
            raise Exception("PyPDF2 is required for PDF merging. Install with: pip install PyPDF2")

        options = options or {}
        files = options.get('files', [input_path])

        try:
            merger = PdfMerger()

            for pdf_file in files:
                merger.append(pdf_file)

            merger.write(output_path)
            merger.close()

            return True
        except Exception as e:
            raise Exception(f"PDF merge failed: {str(e)}")


class TextToMarkdownConverter(ConverterBase):
    name = "Text → Markdown"
    description = "Convert plain text files to formatted Markdown"
    input_formats = [".txt"]
    output_formats = [".md"]
    icon = "📝"

    def convert(self, input_path: str, output_path: str, options: Dict = None) -> bool:
        options = options or {}
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                text_content = f.read()

            # Apply formatting enhancements
            md_content = self._enhance_text(text_content, options)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)

            return True
        except Exception as e:
            raise Exception(f"Text to Markdown conversion failed: {str(e)}")

    def _enhance_text(self, text: str, options: Dict) -> str:
        """Apply markdown formatting enhancements"""
        lines = text.split('\n')
        result = []

        for line in lines:
            # Detect potential headers (all caps lines)
            if options.get('auto_headers', True):
                if line.isupper() and len(line.strip()) > 0 and len(line.strip()) < 80:
                    line = f"## {line.title()}"

            # Detect bullet points
            if options.get('auto_bullets', True):
                if re.match(r'^[\-\*\•]\s', line):
                    line = re.sub(r'^[\-\*\•]\s', '- ', line)
                elif re.match(r'^\d+[\.\)]\s', line):
                    line = re.sub(r'^(\d+)[\.\)]\s', r'\1. ', line)

            result.append(line)

        return '\n'.join(result)


class ExcelToMarkdownConverter(ConverterBase):
    name = "Excel → Markdown Table"
    description = "Convert Excel spreadsheets to Markdown tables"
    input_formats = [".xlsx", ".xls", ".csv"]
    output_formats = [".md"]
    icon = "📊"

    def convert(self, input_path: str, output_path: str, options: Dict = None) -> bool:
        try:
            ext = os.path.splitext(input_path)[1].lower()

            if ext == '.csv':
                with open(input_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    data = list(reader)
            elif PANDAS_AVAILABLE:
                df = pd.read_excel(input_path)
                data = [df.columns.tolist()] + df.values.tolist()
            else:
                raise Exception("pandas is required for Excel files. Install with: pip install pandas openpyxl")

            md_table = self._create_markdown_table(data)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_table)

            return True
        except Exception as e:
            raise Exception(f"Excel to Markdown conversion failed: {str(e)}")

    def _create_markdown_table(self, data: List[List]) -> str:
        """Create a Markdown table from data"""
        if not data:
            return ""

        # Header row
        header = data[0]
        result = ['| ' + ' | '.join(str(cell) for cell in header) + ' |']

        # Separator row
        result.append('| ' + ' | '.join('---' for _ in header) + ' |')

        # Data rows
        for row in data[1:]:
            # Pad row if needed
            while len(row) < len(header):
                row.append('')
            result.append('| ' + ' | '.join(str(cell) for cell in row[:len(header)]) + ' |')

        return '\n'.join(result)


class DocxToMarkdownConverter(ConverterBase):
    name = "Word → Markdown"
    description = "Convert Microsoft Word documents to Markdown"
    input_formats = [".docx"]
    output_formats = [".md"]
    icon = "📃"

    def convert(self, input_path: str, output_path: str, options: Dict = None) -> bool:
        if not DOCX_AVAILABLE:
            raise Exception("python-docx is required for Word conversion. Install with: pip install python-docx")

        try:
            doc = Document(input_path)
            md_content = []

            for para in doc.paragraphs:
                style = para.style.name.lower() if para.style else ""
                text = para.text.strip()

                if not text:
                    md_content.append('')
                    continue

                # Handle headings
                if 'heading 1' in style:
                    md_content.append(f'# {text}')
                elif 'heading 2' in style:
                    md_content.append(f'## {text}')
                elif 'heading 3' in style:
                    md_content.append(f'### {text}')
                elif 'heading' in style:
                    md_content.append(f'#### {text}')
                elif 'list' in style:
                    md_content.append(f'- {text}')
                else:
                    # Check for bold/italic runs
                    formatted_text = self._format_runs(para)
                    md_content.append(formatted_text)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(md_content))

            return True
        except Exception as e:
            raise Exception(f"Word to Markdown conversion failed: {str(e)}")

    def _format_runs(self, para) -> str:
        """Format paragraph runs with bold/italic"""
        result = []
        for run in para.runs:
            text = run.text
            if run.bold:
                text = f'**{text}**'
            if run.italic:
                text = f'*{text}*'
            result.append(text)
        return ''.join(result)


# ============================================================================
# Built-in Cleaners
# ============================================================================

class TTSCleaner(CleanerBase):
    name = "TTS Character Cleaner"
    description = "Clean text for Text-to-Speech engines by removing problematic characters"
    supported_formats = [".txt", ".md"]
    icon = "🔊"

    def clean(self, data: str, options: Dict = None) -> str:
        options = options or {}

        # Remove or replace problematic characters
        result = data

        # Replace common problematic characters
        replacements = {
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '…': '...',
            '—': ' - ',
            '–': ' - ',
            '•': '-',
            '→': 'to',
            '←': 'from',
            '↑': 'up',
            '↓': 'down',
            '©': 'copyright',
            '®': 'registered',
            '™': 'trademark',
            '°': ' degrees',
            '±': 'plus or minus',
            '×': 'times',
            '÷': 'divided by',
            '≈': 'approximately',
            '≠': 'not equal to',
            '≤': 'less than or equal to',
            '≥': 'greater than or equal to',
            '∞': 'infinity',
        }

        for old, new in replacements.items():
            result = result.replace(old, new)

        # Remove URLs if option is set
        if options.get('remove_urls', True):
            result = re.sub(r'https?://\S+', '', result)
            result = re.sub(r'www\.\S+', '', result)

        # Remove email addresses if option is set
        if options.get('remove_emails', True):
            result = re.sub(r'\S+@\S+\.\S+', '', result)

        # Remove markdown formatting if option is set
        if options.get('remove_markdown', True):
            result = re.sub(r'\*\*(.+?)\*\*', r'\1', result)
            result = re.sub(r'\*(.+?)\*', r'\1', result)
            result = re.sub(r'`(.+?)`', r'\1', result)
            result = re.sub(r'^#+\s*', '', result, flags=re.MULTILINE)
            result = re.sub(r'^\s*[-*]\s+', '', result, flags=re.MULTILINE)
            result = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', result)

        # Remove code blocks
        if options.get('remove_code_blocks', True):
            result = re.sub(r'```[\s\S]*?```', '', result)

        # Normalize whitespace
        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r'\n\s*\n', '\n\n', result)

        # Remove non-speakable characters
        result = ''.join(c for c in result if c.isprintable() or c in '\n\t')

        return result.strip()


class PostgresCleaner(CleanerBase):
    name = "Postgres Data Cleaner"
    description = "Clean and escape data for PostgreSQL database insertion"
    supported_formats = [".txt", ".csv", ".json"]
    icon = "🐘"

    def clean(self, data: str, options: Dict = None) -> str:
        options = options or {}

        result = data

        # Escape single quotes (PostgreSQL uses '' for escaping)
        result = result.replace("'", "''")

        # Handle NULL values
        if options.get('convert_empty_to_null', True):
            result = re.sub(r'^$', 'NULL', result, flags=re.MULTILINE)

        # Remove or escape backslashes
        if options.get('escape_backslashes', True):
            result = result.replace('\\', '\\\\')

        # Trim excessive whitespace
        if options.get('trim_whitespace', True):
            lines = result.split('\n')
            result = '\n'.join(line.strip() for line in lines)

        # Remove control characters except newlines and tabs
        result = ''.join(c for c in result if c >= ' ' or c in '\n\t')

        # Handle encoding issues
        if options.get('normalize_unicode', True):
            import unicodedata
            result = unicodedata.normalize('NFKC', result)

        return result


class MarkdownCleaner(CleanerBase):
    name = "Markdown Cleaner"
    description = "Clean and normalize Markdown formatting"
    supported_formats = [".md", ".markdown"]
    icon = "✨"

    def clean(self, data: str, options: Dict = None) -> str:
        options = options or {}

        result = data

        # Normalize line endings
        result = result.replace('\r\n', '\n').replace('\r', '\n')

        # Fix inconsistent header formatting
        if options.get('fix_headers', True):
            result = re.sub(r'^(#+)([^\s#])', r'\1 \2', result, flags=re.MULTILINE)

        # Fix inconsistent list markers
        if options.get('normalize_lists', True):
            result = re.sub(r'^\s*[*+]\s+', '- ', result, flags=re.MULTILINE)

        # Remove trailing whitespace
        if options.get('remove_trailing_whitespace', True):
            result = re.sub(r'[ \t]+$', '', result, flags=re.MULTILINE)

        # Normalize blank lines (max 2 consecutive)
        if options.get('normalize_blank_lines', True):
            result = re.sub(r'\n{3,}', '\n\n', result)

        # Fix broken links
        if options.get('fix_broken_links', True):
            result = re.sub(r'\]\s+\(', '](', result)

        # Add missing language tags to code blocks
        if options.get('detect_code_language', False):
            result = self._detect_and_tag_code(result)

        return result.strip()

    def _detect_and_tag_code(self, text: str) -> str:
        """Detect programming language in code blocks and add tags"""
        def detect_language(code: str) -> str:
            code_lower = code.lower()
            if 'def ' in code_lower or 'import ' in code_lower or 'class ' in code_lower:
                return 'python'
            elif 'function ' in code_lower or 'const ' in code_lower or 'let ' in code_lower:
                return 'javascript'
            elif 'public class' in code_lower or 'private ' in code_lower:
                return 'java'
            elif '#include' in code_lower or 'int main' in code_lower:
                return 'c'
            elif 'SELECT ' in code.upper() or 'INSERT ' in code.upper():
                return 'sql'
            elif '<html' in code_lower or '<div' in code_lower:
                return 'html'
            elif '{' in code and '}' in code and ':' in code:
                return 'json'
            return ''

        def replace_code_block(match):
            existing_lang = match.group(1)
            code = match.group(2)
            if existing_lang:
                return match.group(0)
            detected = detect_language(code)
            return f'```{detected}\n{code}```'

        return re.sub(r'```(\w*)\n([\s\S]*?)```', replace_code_block, text)


class HTMLEntityCleaner(CleanerBase):
    name = "HTML Entity Cleaner"
    description = "Decode HTML entities and clean up HTML artifacts"
    supported_formats = [".txt", ".html", ".md"]
    icon = "🧼"

    def clean(self, data: str, options: Dict = None) -> str:
        options = options or {}

        result = data

        # Decode HTML entities
        result = html.unescape(result)

        # Remove residual HTML tags if requested
        if options.get('strip_tags', True):
            result = re.sub(r'<[^>]+>', '', result)

        # Clean up common HTML artifacts
        if options.get('clean_artifacts', True):
            result = result.replace('&nbsp;', ' ')
            result = result.replace('&#8203;', '')  # Zero-width space
            result = re.sub(r'<!--[\s\S]*?-->', '', result)

        return result


# ============================================================================
# Register Built-in Plugins
# ============================================================================

# Register converters
PluginRegistry.register_converter(MarkdownToHTMLConverter())
PluginRegistry.register_converter(HTMLToMarkdownConverter())
PluginRegistry.register_converter(HTMLToExcelConverter())
PluginRegistry.register_converter(PDFToTextConverter())
PluginRegistry.register_converter(PDFMergeConverter())
PluginRegistry.register_converter(TextToMarkdownConverter())
PluginRegistry.register_converter(ExcelToMarkdownConverter())
PluginRegistry.register_converter(DocxToMarkdownConverter())

# Register cleaners
PluginRegistry.register_cleaner(TTSCleaner())
PluginRegistry.register_cleaner(PostgresCleaner())
PluginRegistry.register_cleaner(MarkdownCleaner())
PluginRegistry.register_cleaner(HTMLEntityCleaner())


# ============================================================================
# Main Application
# ============================================================================

class ConversionHub(ctk.CTk):
    """Main application window for Conversion & Data Cleaning Hub"""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("Conversion & Data Cleaning Hub")
        self.geometry("1300x900")
        self.minsize(1000, 700)

        # State
        self.current_files = []
        self.current_converter = None
        self.current_cleaner = None
        self.processing = False
        self.config_file = Path.home() / ".conversion_hub_config.json"

        # Load configuration
        self.load_config()

        # Create UI
        self.create_widgets()

        # Check dependencies
        self.check_dependencies()

    def load_config(self):
        """Load configuration from file"""
        self.config = {
            'last_input_dir': os.path.expanduser("~"),
            'last_output_dir': os.path.expanduser("~"),
        }
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config.update(json.load(f))
            except Exception:
                pass

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def create_widgets(self):
        """Create all UI widgets"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left sidebar - Tools selection
        self.create_sidebar()

        # Main content area
        self.create_main_area()

    def create_sidebar(self):
        """Create the left sidebar with tool categories"""
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        # App title
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="Conversion Hub",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 5))

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar,
            text="Convert • Clean • Transform",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Tool category tabs
        self.tabview = ctk.CTkTabview(self.sidebar, width=280)
        self.tabview.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.sidebar.grid_rowconfigure(2, weight=1)

        # Converters tab
        self.tab_converters = self.tabview.add("Converters")
        self.create_converters_list()

        # Cleaners tab
        self.tab_cleaners = self.tabview.add("Cleaners")
        self.create_cleaners_list()

        # Dependencies status
        self.deps_frame = ctk.CTkFrame(self.sidebar)
        self.deps_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.deps_label = ctk.CTkLabel(
            self.deps_frame,
            text="Dependencies",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.deps_label.pack(pady=(10, 5))

        self.deps_status = ctk.CTkLabel(
            self.deps_frame,
            text="Checking...",
            font=ctk.CTkFont(size=10),
            wraplength=260
        )
        self.deps_status.pack(pady=(0, 10), padx=10)

    def create_converters_list(self):
        """Create the converters list"""
        self.converters_frame = ctk.CTkScrollableFrame(self.tab_converters)
        self.converters_frame.pack(fill="both", expand=True, padx=5, pady=5)

        for converter in PluginRegistry.converters:
            btn = ctk.CTkButton(
                self.converters_frame,
                text=f"{converter.icon} {converter.name}",
                command=lambda c=converter: self.select_converter(c),
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                height=35
            )
            btn.pack(fill="x", pady=2)

    def create_cleaners_list(self):
        """Create the cleaners list"""
        self.cleaners_frame = ctk.CTkScrollableFrame(self.tab_cleaners)
        self.cleaners_frame.pack(fill="both", expand=True, padx=5, pady=5)

        for cleaner in PluginRegistry.cleaners:
            btn = ctk.CTkButton(
                self.cleaners_frame,
                text=f"{cleaner.icon} {cleaner.name}",
                command=lambda c=cleaner: self.select_cleaner(c),
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                height=35
            )
            btn.pack(fill="x", pady=2)

    def create_main_area(self):
        """Create the main content area"""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # Header section
        self.header_frame = ctk.CTkFrame(self.main_frame)
        self.header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.tool_title = ctk.CTkLabel(
            self.header_frame,
            text="Select a Tool",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.tool_title.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.tool_description = ctk.CTkLabel(
            self.header_frame,
            text="Choose a converter or cleaner from the sidebar to get started",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.tool_description.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")

        # Input section
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)

        self.input_label = ctk.CTkLabel(
            self.input_frame,
            text="Input Files:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.input_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.files_listbox = ctk.CTkTextbox(self.input_frame, height=100)
        self.files_listbox.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.files_listbox.configure(state="disabled")

        self.input_buttons_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.input_buttons_frame.grid(row=0, column=2, padx=10, pady=10)

        self.add_files_btn = ctk.CTkButton(
            self.input_buttons_frame,
            text="Add Files",
            command=self.add_files,
            width=100
        )
        self.add_files_btn.grid(row=0, column=0, pady=2)

        self.add_folder_btn = ctk.CTkButton(
            self.input_buttons_frame,
            text="Add Folder",
            command=self.add_folder,
            width=100
        )
        self.add_folder_btn.grid(row=1, column=0, pady=2)

        self.clear_files_btn = ctk.CTkButton(
            self.input_buttons_frame,
            text="Clear",
            command=self.clear_files,
            width=100,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.clear_files_btn.grid(row=2, column=0, pady=2)

        # Options and output section
        self.work_frame = ctk.CTkFrame(self.main_frame)
        self.work_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.work_frame.grid_columnconfigure(0, weight=1)
        self.work_frame.grid_columnconfigure(1, weight=1)
        self.work_frame.grid_rowconfigure(1, weight=1)

        # Options panel
        self.options_label = ctk.CTkLabel(
            self.work_frame,
            text="Options",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.options_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.options_frame = ctk.CTkScrollableFrame(self.work_frame)
        self.options_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Output/Preview panel
        self.output_label = ctk.CTkLabel(
            self.work_frame,
            text="Output / Log",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.output_label.grid(row=0, column=1, padx=15, pady=(15, 5), sticky="w")

        self.output_text = ctk.CTkTextbox(
            self.work_frame,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.output_text.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Action buttons
        self.action_frame = ctk.CTkFrame(self.main_frame)
        self.action_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.action_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(self.action_frame)
        self.progress_bar.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        self.progress_bar.set(0)

        self.buttons_frame = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        self.buttons_frame.grid(row=1, column=0, pady=10)

        self.process_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Process",
            command=self.process_files,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#22c55e",
            hover_color="#16a34a"
        )
        self.process_btn.grid(row=0, column=0, padx=10)

        self.preview_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Preview",
            command=self.preview_output,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#6366f1",
            hover_color="#4f46e5"
        )
        self.preview_btn.grid(row=0, column=1, padx=10)

    def select_converter(self, converter: ConverterBase):
        """Select a converter tool"""
        self.current_converter = converter
        self.current_cleaner = None

        self.tool_title.configure(text=f"{converter.icon} {converter.name}")
        self.tool_description.configure(text=converter.description)

        # Update input format hint
        formats = ', '.join(converter.input_formats)
        self.input_label.configure(text=f"Input Files ({formats}):")

        # Clear and update options
        self.update_options_panel(converter)

        self.log_output(f"Selected converter: {converter.name}")

    def select_cleaner(self, cleaner: CleanerBase):
        """Select a cleaner tool"""
        self.current_cleaner = cleaner
        self.current_converter = None

        self.tool_title.configure(text=f"{cleaner.icon} {cleaner.name}")
        self.tool_description.configure(text=cleaner.description)

        # Update input format hint
        formats = ', '.join(cleaner.supported_formats)
        self.input_label.configure(text=f"Input Files ({formats}):")

        # Clear and update options
        self.update_options_panel(cleaner)

        self.log_output(f"Selected cleaner: {cleaner.name}")

    def update_options_panel(self, tool):
        """Update the options panel for the selected tool"""
        # Clear existing options
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        self.option_vars = {}

        # Add common options based on tool type
        if isinstance(tool, ConverterBase):
            self.create_converter_options(tool)
        elif isinstance(tool, CleanerBase):
            self.create_cleaner_options(tool)

    def create_converter_options(self, converter: ConverterBase):
        """Create options for a converter"""
        # Output directory
        self.output_dir_label = ctk.CTkLabel(
            self.options_frame,
            text="Output Directory:",
            font=ctk.CTkFont(size=12)
        )
        self.output_dir_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.output_dir_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.output_dir_frame.pack(fill="x", padx=10, pady=5)

        self.output_dir_var = ctk.StringVar(value=self.config.get('last_output_dir', ''))
        self.output_dir_entry = ctk.CTkEntry(
            self.output_dir_frame,
            textvariable=self.output_dir_var,
            width=200
        )
        self.output_dir_entry.pack(side="left", fill="x", expand=True)

        self.output_dir_btn = ctk.CTkButton(
            self.output_dir_frame,
            text="Browse",
            command=self.browse_output_dir,
            width=70
        )
        self.output_dir_btn.pack(side="right", padx=(5, 0))

        # Converter-specific options
        if isinstance(converter, MarkdownToHTMLConverter):
            self.option_vars['include_styles'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Include CSS Styles",
                variable=self.option_vars['include_styles']
            ).pack(anchor="w", padx=10, pady=5)

            self.option_vars['dark_mode'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Dark Mode Theme",
                variable=self.option_vars['dark_mode']
            ).pack(anchor="w", padx=10, pady=5)

        elif isinstance(converter, TextToMarkdownConverter):
            self.option_vars['auto_headers'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Auto-detect Headers",
                variable=self.option_vars['auto_headers']
            ).pack(anchor="w", padx=10, pady=5)

            self.option_vars['auto_bullets'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Auto-format Bullet Points",
                variable=self.option_vars['auto_bullets']
            ).pack(anchor="w", padx=10, pady=5)

    def create_cleaner_options(self, cleaner: CleanerBase):
        """Create options for a cleaner"""
        # Output settings
        self.option_vars['overwrite'] = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self.options_frame,
            text="Overwrite Original Files",
            variable=self.option_vars['overwrite']
        ).pack(anchor="w", padx=10, pady=5)

        self.output_dir_label = ctk.CTkLabel(
            self.options_frame,
            text="Output Directory (if not overwriting):",
            font=ctk.CTkFont(size=12)
        )
        self.output_dir_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.output_dir_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.output_dir_frame.pack(fill="x", padx=10, pady=5)

        self.output_dir_var = ctk.StringVar(value=self.config.get('last_output_dir', ''))
        self.output_dir_entry = ctk.CTkEntry(
            self.output_dir_frame,
            textvariable=self.output_dir_var,
            width=200
        )
        self.output_dir_entry.pack(side="left", fill="x", expand=True)

        self.output_dir_btn = ctk.CTkButton(
            self.output_dir_frame,
            text="Browse",
            command=self.browse_output_dir,
            width=70
        )
        self.output_dir_btn.pack(side="right", padx=(5, 0))

        # Cleaner-specific options
        if isinstance(cleaner, TTSCleaner):
            self.option_vars['remove_urls'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Remove URLs",
                variable=self.option_vars['remove_urls']
            ).pack(anchor="w", padx=10, pady=5)

            self.option_vars['remove_emails'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Remove Email Addresses",
                variable=self.option_vars['remove_emails']
            ).pack(anchor="w", padx=10, pady=5)

            self.option_vars['remove_markdown'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Remove Markdown Formatting",
                variable=self.option_vars['remove_markdown']
            ).pack(anchor="w", padx=10, pady=5)

            self.option_vars['remove_code_blocks'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Remove Code Blocks",
                variable=self.option_vars['remove_code_blocks']
            ).pack(anchor="w", padx=10, pady=5)

        elif isinstance(cleaner, PostgresCleaner):
            self.option_vars['convert_empty_to_null'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Convert Empty to NULL",
                variable=self.option_vars['convert_empty_to_null']
            ).pack(anchor="w", padx=10, pady=5)

            self.option_vars['escape_backslashes'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Escape Backslashes",
                variable=self.option_vars['escape_backslashes']
            ).pack(anchor="w", padx=10, pady=5)

            self.option_vars['trim_whitespace'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Trim Whitespace",
                variable=self.option_vars['trim_whitespace']
            ).pack(anchor="w", padx=10, pady=5)

            self.option_vars['normalize_unicode'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Normalize Unicode",
                variable=self.option_vars['normalize_unicode']
            ).pack(anchor="w", padx=10, pady=5)

        elif isinstance(cleaner, MarkdownCleaner):
            self.option_vars['fix_headers'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Fix Header Formatting",
                variable=self.option_vars['fix_headers']
            ).pack(anchor="w", padx=10, pady=5)

            self.option_vars['normalize_lists'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Normalize List Markers",
                variable=self.option_vars['normalize_lists']
            ).pack(anchor="w", padx=10, pady=5)

            self.option_vars['remove_trailing_whitespace'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Remove Trailing Whitespace",
                variable=self.option_vars['remove_trailing_whitespace']
            ).pack(anchor="w", padx=10, pady=5)

            self.option_vars['normalize_blank_lines'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Normalize Blank Lines",
                variable=self.option_vars['normalize_blank_lines']
            ).pack(anchor="w", padx=10, pady=5)

        elif isinstance(cleaner, HTMLEntityCleaner):
            self.option_vars['strip_tags'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Strip HTML Tags",
                variable=self.option_vars['strip_tags']
            ).pack(anchor="w", padx=10, pady=5)

            self.option_vars['clean_artifacts'] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Clean HTML Artifacts",
                variable=self.option_vars['clean_artifacts']
            ).pack(anchor="w", padx=10, pady=5)

    def browse_output_dir(self):
        """Browse for output directory"""
        folder = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.config.get('last_output_dir', os.path.expanduser("~"))
        )
        if folder:
            self.output_dir_var.set(folder)
            self.config['last_output_dir'] = folder
            self.save_config()

    def add_files(self):
        """Add files to process"""
        filetypes = [("All files", "*.*")]

        if self.current_converter:
            exts = ' '.join(f'*{ext}' for ext in self.current_converter.input_formats)
            filetypes.insert(0, (f"Supported files", exts))
        elif self.current_cleaner:
            exts = ' '.join(f'*{ext}' for ext in self.current_cleaner.supported_formats)
            filetypes.insert(0, (f"Supported files", exts))

        files = filedialog.askopenfilenames(
            title="Select Files",
            initialdir=self.config.get('last_input_dir', os.path.expanduser("~")),
            filetypes=filetypes
        )

        if files:
            self.current_files.extend(files)
            self.config['last_input_dir'] = os.path.dirname(files[0])
            self.save_config()
            self.update_files_list()

    def add_folder(self):
        """Add all files from a folder"""
        folder = filedialog.askdirectory(
            title="Select Folder",
            initialdir=self.config.get('last_input_dir', os.path.expanduser("~"))
        )

        if folder:
            exts = []
            if self.current_converter:
                exts = self.current_converter.input_formats
            elif self.current_cleaner:
                exts = self.current_cleaner.supported_formats

            for root, dirs, files in os.walk(folder):
                for file in files:
                    if not exts or any(file.lower().endswith(ext) for ext in exts):
                        self.current_files.append(os.path.join(root, file))

            self.config['last_input_dir'] = folder
            self.save_config()
            self.update_files_list()

    def clear_files(self):
        """Clear the file list"""
        self.current_files = []
        self.update_files_list()

    def update_files_list(self):
        """Update the files listbox"""
        self.files_listbox.configure(state="normal")
        self.files_listbox.delete("1.0", "end")

        if self.current_files:
            for f in self.current_files:
                self.files_listbox.insert("end", f"{f}\n")
        else:
            self.files_listbox.insert("end", "No files selected")

        self.files_listbox.configure(state="disabled")

    def get_options(self) -> Dict:
        """Get current options as dictionary"""
        options = {}
        for key, var in self.option_vars.items():
            if isinstance(var, ctk.BooleanVar):
                options[key] = var.get()
            elif isinstance(var, ctk.StringVar):
                options[key] = var.get()
        return options

    def process_files(self):
        """Process the files"""
        if not self.current_files:
            messagebox.showwarning("No Files", "Please add files to process")
            return

        if not self.current_converter and not self.current_cleaner:
            messagebox.showwarning("No Tool", "Please select a converter or cleaner")
            return

        if self.processing:
            return

        self.processing = True
        self.process_btn.configure(state="disabled")

        def run_processing():
            try:
                options = self.get_options()
                output_dir = self.output_dir_var.get() if hasattr(self, 'output_dir_var') else ''

                if not output_dir and not options.get('overwrite', False):
                    output_dir = os.path.dirname(self.current_files[0])

                total = len(self.current_files)
                success = 0
                failed = 0

                for i, input_file in enumerate(self.current_files):
                    try:
                        progress = (i + 1) / total
                        self.progress_bar.set(progress)

                        if self.current_converter:
                            # Determine output file
                            base_name = os.path.splitext(os.path.basename(input_file))[0]
                            out_ext = self.current_converter.output_formats[0]
                            output_file = os.path.join(output_dir, f"{base_name}{out_ext}")

                            self.log_output(f"Converting: {input_file}")
                            self.current_converter.convert(input_file, output_file, options)
                            self.log_output(f"  -> {output_file}")

                        elif self.current_cleaner:
                            # Read file
                            with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
                                data = f.read()

                            # Clean
                            cleaned = self.current_cleaner.clean(data, options)

                            # Write output
                            if options.get('overwrite', False):
                                output_file = input_file
                            else:
                                base_name = os.path.basename(input_file)
                                output_file = os.path.join(output_dir, f"cleaned_{base_name}")

                            with open(output_file, 'w', encoding='utf-8') as f:
                                f.write(cleaned)

                            self.log_output(f"Cleaned: {input_file}")
                            self.log_output(f"  -> {output_file}")

                        success += 1

                    except Exception as e:
                        failed += 1
                        self.log_output(f"Error processing {input_file}: {str(e)}")

                self.log_output(f"\n{'='*50}")
                self.log_output(f"Processing complete: {success} succeeded, {failed} failed")
                self.log_output(f"{'='*50}\n")

            except Exception as e:
                self.log_output(f"Processing error: {str(e)}")

            finally:
                self.processing = False
                self.process_btn.configure(state="normal")
                self.progress_bar.set(0)

        thread = threading.Thread(target=run_processing)
        thread.daemon = True
        thread.start()

    def preview_output(self):
        """Preview the output for the first file"""
        if not self.current_files:
            messagebox.showwarning("No Files", "Please add files to preview")
            return

        if not self.current_converter and not self.current_cleaner:
            messagebox.showwarning("No Tool", "Please select a converter or cleaner")
            return

        try:
            input_file = self.current_files[0]
            options = self.get_options()

            self.log_output(f"\n{'='*50}")
            self.log_output(f"Preview for: {input_file}")
            self.log_output(f"{'='*50}\n")

            if self.current_converter:
                # Create temp output file
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix=self.current_converter.output_formats[0],
                    delete=False
                ) as tmp:
                    tmp_path = tmp.name

                self.current_converter.convert(input_file, tmp_path, options)

                with open(tmp_path, 'r', encoding='utf-8', errors='replace') as f:
                    preview = f.read()

                os.unlink(tmp_path)

                # Show first 2000 chars
                if len(preview) > 2000:
                    preview = preview[:2000] + "\n\n... (truncated) ..."

                self.log_output(preview)

            elif self.current_cleaner:
                with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
                    data = f.read()

                cleaned = self.current_cleaner.clean(data, options)

                # Show first 2000 chars
                if len(cleaned) > 2000:
                    cleaned = cleaned[:2000] + "\n\n... (truncated) ..."

                self.log_output("=== ORIGINAL (first 500 chars) ===")
                self.log_output(data[:500] if len(data) > 500 else data)
                self.log_output("\n=== CLEANED ===")
                self.log_output(cleaned)

        except Exception as e:
            self.log_output(f"Preview error: {str(e)}")

    def log_output(self, message: str):
        """Log a message to the output panel"""
        self.output_text.configure(state="normal")
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")

    def check_dependencies(self):
        """Check and display dependency status"""
        deps = []
        if MARKDOWN_AVAILABLE:
            deps.append("markdown")
        if BS4_AVAILABLE:
            deps.append("beautifulsoup4")
        if PANDAS_AVAILABLE:
            deps.append("pandas")
        if PYPDF2_AVAILABLE:
            deps.append("PyPDF2")
        if OPENPYXL_AVAILABLE:
            deps.append("openpyxl")
        if DOCX_AVAILABLE:
            deps.append("python-docx")

        missing = []
        if not MARKDOWN_AVAILABLE:
            missing.append("markdown")
        if not BS4_AVAILABLE:
            missing.append("beautifulsoup4")
        if not PANDAS_AVAILABLE:
            missing.append("pandas")
        if not PYPDF2_AVAILABLE:
            missing.append("PyPDF2")

        status_text = f"Installed: {', '.join(deps) if deps else 'None'}"
        if missing:
            status_text += f"\n\nOptional: {', '.join(missing)}"

        self.deps_status.configure(text=status_text)


def main():
    app = ConversionHub()
    app.mainloop()


if __name__ == "__main__":
    main()
