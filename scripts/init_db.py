"""Initialize local SQLite database for Materia Content Studio.

Usage:
    PYTHONPATH=src python scripts/init_db.py
"""

from materia_content_studio.config import get_settings
from materia_content_studio.db import Database


def main() -> None:
    settings = get_settings()
    db = Database(settings.database_path)
    db.init()
    print(f"Database initialized at: {settings.database_path}")


if __name__ == "__main__":
    main()
