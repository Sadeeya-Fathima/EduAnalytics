
"""Create and verify a readable, timestamped SQLite backup."""

import argparse
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "instance" / "eduanalytics.db"
DEFAULT_BACKUP_DIR = PROJECT_ROOT.parent / "EduAnalytics_Backups"
METADATA_TABLE = "_eduanalytics_backup_metadata"


def integrity_check(connection: sqlite3.Connection) -> None:
    result = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if result != "ok":
        raise RuntimeError(f"Integrity check failed: {result}")


def read_institution_name(connection: sqlite3.Connection) -> str | None:
    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    if "institution" not in tables:
        return None

    rows = connection.execute(
        "SELECT name FROM institution ORDER BY id"
    ).fetchall()
    if len(rows) != 1 or not rows[0][0].strip():
        raise RuntimeError(
            "Expected exactly one institution with a non-empty name."
        )
    return rows[0][0].strip()


def safe_filename(value: str) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value)
    value = re.sub(r"\s+", "_", value.strip()).strip("._")
    return value[:80] or "Institution"



def create_backup(source: Path, backup_dir: Path) -> Path:
    """Create a consistent backup and verify its integrity."""
    if not source.is_file():
        raise FileNotFoundError(f"Database not found: {source}")

    backup_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now().astimezone()
    created_at = now.isoformat(timespec="seconds")

    original = sqlite3.connect(str(source), timeout=30)
    try:
        institution = read_institution_name(original)
        label = safe_filename(institution or "SQLite_Database")
        filename = (
            f"{label}_{now.strftime('%Y-%m-%d_%I-%M-%S_%f_%p')}.db"
        )
        destination = backup_dir / filename

        # Exclusive creation avoids overwriting an existing backup.
        with destination.open("xb"):
            pass

        try:
            backup = sqlite3.connect(str(destination), timeout=30)
            try:
                original.backup(backup)

                if institution is not None:
                    backup.execute(
                        f"""
                        CREATE TABLE "{METADATA_TABLE}" (
                            id INTEGER PRIMARY KEY CHECK (id = 1),
                            institution_name TEXT NOT NULL,
                            created_at TEXT NOT NULL,
                            format_version INTEGER NOT NULL
                        )
                        """
                    )
                    backup.execute(
                        f"""
                        INSERT INTO "{METADATA_TABLE}"
                        (id, institution_name, created_at, format_version)
                        VALUES (1, ?, ?, 1)
                        """,
                        (institution, created_at),
                    )

                backup.commit()
                integrity_check(backup)
            finally:
                backup.close()

            uri = destination.resolve().as_uri() + "?mode=ro"
            verified = sqlite3.connect(uri, uri=True)
            try:
                integrity_check(verified)

                if institution is not None:
                    metadata = verified.execute(
                        f"""
                        SELECT institution_name, created_at, format_version
                        FROM "{METADATA_TABLE}" WHERE id = 1
                        """
                    ).fetchone()
                    if metadata != (institution, created_at, 1):
                        raise RuntimeError(
                            "Backup metadata verification failed."
                        )
            finally:
                verified.close()

            return destination

        except Exception:
            try:
                destination.unlink(missing_ok=True)
            except OSError:
                pass
            raise
    finally:
        original.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create and verify an EduAnalytics database backup."
    )
    parser.add_argument(
        "--destination-dir",
        type=Path,
        default=DEFAULT_BACKUP_DIR,
        help="Backup folder (default: sibling EduAnalytics_Backups folder).",
    )
    args = parser.parse_args()

    try:
        destination = create_backup(DATABASE_PATH, args.destination_dir)
    except Exception as exc:
        print(f"ERROR: Backup failed: {exc}", file=sys.stderr)
        return 1

    print("EduAnalytics - Database Backup")
    print(f"Backup file : {destination.name}")
    print(f"Location    : {destination.parent}")
    print("Status      : Successful")
    print("Integrity   : Verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
