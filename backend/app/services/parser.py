import os
from typing import Optional
from PyPDF2 import PdfReader
from docx import Document
import logging
from pdf2image import convert_from_path
from PIL import Image
import re

class DocumentParser:
    """Parser service for extracting text from PDF and DOCX files."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract_text(self, file_path: str) -> Optional[str]:
        """
        Extract text from a document file (PDF or DOCX).
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text as string, or None if extraction fails
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return None

        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_extension == '.docx':
                return self._extract_from_docx(file_path)
            else:
                self.logger.error(f"Unsupported file format: {file_extension}")
                return None
        except Exception as e:
            self.logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return None

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = []
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    # Fix spaced text
                    page_text = self._fix_spaced_text(page_text)
                    text.append(page_text)
        return '\n'.join(text)

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        doc = Document(file_path)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing extra whitespace and normalizing line endings.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
            
        # Replace multiple newlines with single newline
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        
        # Replace multiple spaces with single space
        text = ' '.join(text.split())
        
        return text

    def parse_document(self, file_path: str) -> Optional[str]:
        """
        Parse a document and return cleaned text.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Cleaned text content, or None if parsing fails
        """
        raw_text = self.extract_text(file_path)
        if raw_text is None:
            return None
            
        return self.clean_text(raw_text)

    def _fix_spaced_text(self, text: str) -> str:
        fixed_lines = []
        for line in text.splitlines():
            words = line.split()
            # If more than 70% of words are single characters, join them
            if len(words) > 0 and sum(len(w) == 1 for w in words) / len(words) > 0.7:
                # Join single characters into words, but keep numbers and emails intact
                joined = ''.join(words)
                # Try to restore spaces between email/URLs/numbers if needed
                # (Optional: add more sophisticated logic here)
                fixed_lines.append(joined)
            else:
                fixed_lines.append(line)
        return '\n'.join(fixed_lines)
 