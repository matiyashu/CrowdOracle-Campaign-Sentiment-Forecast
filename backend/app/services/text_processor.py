"""
Text processing service.
"""

from typing import List
from ..utils.file_parser import FileParser, split_text_into_chunks


class TextProcessor:
    """Text processor — extracts, splits, and cleans document text."""

    @staticmethod
    def extract_from_files(file_paths: List[str]) -> str:
        """Extract and concatenate text from multiple files."""
        return FileParser.extract_from_multiple(file_paths)

    @staticmethod
    def split_text(
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Raw input text
            chunk_size: Target chunk size in characters
            overlap: Overlap between consecutive chunks

        Returns:
            List of text chunks
        """
        return split_text_into_chunks(text, chunk_size, overlap)

    @staticmethod
    def preprocess_text(text: str) -> str:
        """
        Clean and normalize text.
        - Normalize line endings
        - Collapse excessive blank lines (max two newlines)
        - Strip leading/trailing whitespace from each line

        Args:
            text: Raw input text

        Returns:
            Cleaned text
        """
        import re

        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Collapse runs of blank lines (keep at most two newlines)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)

        return text.strip()

    @staticmethod
    def get_text_stats(text: str) -> dict:
        """Return basic statistics (chars, lines, words) for a text string."""
        return {
            "total_chars": len(text),
            "total_lines": text.count('\n') + 1,
            "total_words": len(text.split()),
        }

