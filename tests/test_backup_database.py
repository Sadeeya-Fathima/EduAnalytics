import sqlite3
from pathlib import Path

import pytest

from scripts.backup_database import create_backup


def create_test_database(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TABLE sample_records (id INTEGER PRIMARY KEY, name TEXT)"
        )
        connection.execute(
            "INSERT INTO sample_records (name) VALUES (?)",
            ("test-record",),
        )


def test_backup_preserves_database_contents(tmp_path):
    source = tmp_path / "source.db"
    backup_dir = tmp_path / "backups"
    create_test_database(source)

    backup = create_backup(source, backup_dir)

    assert backup.is_file()
    assert backup.parent == backup_dir
    with sqlite3.connect(backup) as connection:
        assert connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0] == "ok"
        assert connection.execute(
            "SELECT name FROM sample_records"
        ).fetchone()[0] == "test-record"


def test_backup_uses_unique_timestamped_names(tmp_path):
    source = tmp_path / "source.db"
    backup_dir = tmp_path / "backups"
    create_test_database(source)

    first = create_backup(source, backup_dir)
    second = create_backup(source, backup_dir)

    assert first != second
    assert first.is_file()
    assert second.is_file()


def test_missing_source_fails_without_creating_backup(tmp_path):
    source = tmp_path / "missing.db"
    backup_dir = tmp_path / "backups"

    with pytest.raises(FileNotFoundError):
        create_backup(source, backup_dir)

    assert not backup_dir.exists()


def test_backup_contains_same_table_names(tmp_path):
    source = tmp_path / "source.db"
    backup_dir = tmp_path / "backups"
    create_test_database(source)

    backup = create_backup(source, backup_dir)

    def table_names(path):
        with sqlite3.connect(path) as connection:
            return {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }

    assert table_names(backup) == table_names(source)
