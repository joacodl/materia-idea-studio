from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


class BrandManualParser:
    @staticmethod
    def parse_file(path: Path) -> str:
        if path.suffix.lower() == ".txt":
            return path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".pdf":
            reader = PdfReader(str(path))
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        return ""
