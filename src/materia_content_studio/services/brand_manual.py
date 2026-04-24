from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


class BrandManualParser:
    @staticmethod
    def parse_file(path: Path) -> str:
class BrandManualService:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def save_uploaded_file(self, filename: str, content: bytes) -> Path:
        output_path = self.storage_path.parent / filename
        output_path.write_bytes(content)
        self.storage_path.write_text(str(output_path), encoding="utf-8")
        return output_path

    def get_manual_text(self) -> str:
        if not self.storage_path.exists():
            return ""
        path = Path(self.storage_path.read_text(encoding="utf-8").strip())
        if not path.exists():
            return ""
        if path.suffix.lower() == ".txt":
            return path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".pdf":
            reader = PdfReader(str(path))
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        return ""
