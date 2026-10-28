
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from scripts import restore_database as recovery


def create_database(path: Path, institution: str = "EduAnalytics") -> None:
    with closing(sqlite3.connect(path)) as connection:
        connection.execute(
            "CREATE TABLE institution "
            "(id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO institution (name) VALUES (?)",
            (institution,),
        )
        connection.execute(
            "CREATE TABLE student_records "
            "(id INTEGER PRIMARY KEY, student_name TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO student_records (student_name) VALUES (?)",
            ("Test Student",),
        )
        connection.commit()


def get_student_name(path: Path) -> str:
    with closing(sqlite3.connect(path)) as connection:
        return connection.execute(
            "SELECT student_name FROM student_records"
        ).fetchone()[0]


def assert_database_integrity(path: Path) -> None:
    with closing(sqlite3.connect(path)) as connection:
        assert connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0] == "ok"


def test_inspect_backup_reads_institution_and_timestamp(tmp_path, monkeypatch):
    source = tmp_path / "source.db"
    backup_dir = tmp_path / "backups"
    create_database(source)

    monkeypatch.setattr(
        recovery, "METADATA_TABLE", "_eduanalytics_backup_metadata"
    )

    backup = recovery.create_backup(source, backup_dir)
    details = recovery.inspect_backup(backup)

    assert details["institution"] == "EduAnalytics"
    assert details["path"] == backup
    assert details["timestamp"]


def test_inspect_backup_rejects_corrupt_database(tmp_path):
    corrupt_backup = tmp_path / "corrupt.db"
    corrupt_backup.write_bytes(b"not a valid SQLite database")

    with pytest.raises((sqlite3.DatabaseError, RuntimeError)):
        recovery.inspect_backup(corrupt_backup)


def test_prepare_restored_database_preserves_records_and_removes_metadata(
    tmp_path,
):
    source = tmp_path / "source.db"
    backup_dir = tmp_path / "backups"
    staging = tmp_path / "staging.db"
    create_database(source)

    backup = recovery.create_backup(source, backup_dir)
    recovery.prepare_restored_database(backup, staging)

    assert_database_integrity(staging)

    with closing(sqlite3.connect(staging)) as connection:
        assert connection.execute(
            "SELECT name FROM institution"
        ).fetchone()[0] == "EduAnalytics"

        assert connection.execute(
            "SELECT student_name FROM student_records"
        ).fetchone()[0] == "Test Student"

        table_names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }

        assert "_eduanalytics_backup_metadata" not in table_names


def test_prepare_restored_database_accepts_valid_named_institution(tmp_path):
    source = tmp_path / "source.db"
    staging = tmp_path / "staging.db"
    create_database(source, institution="Different Institution")

    recovery.prepare_restored_database(source, staging)

    with closing(sqlite3.connect(staging)) as connection:
        assert connection.execute(
            "SELECT name FROM institution"
        ).fetchone()[0] == "Different Institution"


def test_replace_live_database_swaps_files(tmp_path):
    live = tmp_path / "live.db"
    staging = tmp_path / "staging.db"
    rollback = tmp_path / "rollback.db"

    live.write_text("old database", encoding="utf-8")
    staging.write_text("new database", encoding="utf-8")

    recovery.replace_live_database(staging, live, rollback)

    assert live.read_text(encoding="utf-8") == "new database"
    assert rollback.read_text(encoding="utf-8") == "old database"
    assert not staging.exists()


def test_cancelled_recovery_does_not_change_live_database(
    tmp_path, monkeypatch, capsys
):
    live = tmp_path / "live.db"
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    create_database(live)

    recovery.create_backup(live, backup_dir)
    original_bytes = live.read_bytes()

    monkeypatch.setattr(recovery, "DATABASE_PATH", live)
    monkeypatch.setattr(recovery, "DEFAULT_BACKUP_DIR", backup_dir)
    monkeypatch.setattr(recovery, "server_appears_running", lambda: False)
    monkeypatch.setattr("builtins.input", lambda _prompt: "q")

    result = recovery.main()
    captured = capsys.readouterr()

    assert result == 0
    assert live.read_bytes() == original_bytes
    assert "Recovery cancelled" in captured.out


def test_end_to_end_recovery_restores_records_and_retains_safety_copies(
    tmp_path, monkeypatch, capsys
):
    live = tmp_path / "live.db"
    restore_source = tmp_path / "restore_source.db"
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    create_database(live)
    with closing(sqlite3.connect(live)) as connection:
        connection.execute(
            "UPDATE student_records SET student_name = ?",
            ("Original Student",),
        )
        connection.commit()

    create_database(restore_source)
    with closing(sqlite3.connect(restore_source)) as connection:
        connection.execute(
            "UPDATE student_records SET student_name = ?",
            ("Restored Student",),
        )
        connection.commit()

    selected_backup = recovery.create_backup(restore_source, backup_dir)

    monkeypatch.setattr(recovery, "DATABASE_PATH", live)
    monkeypatch.setattr(recovery, "DEFAULT_BACKUP_DIR", backup_dir)
    monkeypatch.setattr(recovery, "server_appears_running", lambda: False)

    answers = iter(["1", "RESTORE"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    result = recovery.main()
    captured = capsys.readouterr()
    output = captured.out
    error_output = captured.err

    assert result == 0, f"STDOUT:\n{output}\nSTDERR:\n{error_output}"
    assert "Recovery completed successfully." in output
    assert "Integrity: Verified" in output
    assert selected_backup.name in output

    assert_database_integrity(live)
    assert get_student_name(live) == "Restored Student"

    backup_files = list(backup_dir.glob("*.db"))
    assert len(backup_files) >= 2

    safety_backups = [
        path for path in backup_files if path != selected_backup
    ]
    assert safety_backups

    assert_database_integrity(safety_backups[0])
    assert get_student_name(safety_backups[0]) == "Original Student"

    rollback_files = list(tmp_path.glob(".live_rollback_*.db"))
    assert len(rollback_files) == 1
    assert_database_integrity(rollback_files[0])
    assert get_student_name(rollback_files[0]) == "Original Student"


def test_end_to_end_recovery_failure_restores_original_database(
    tmp_path, monkeypatch, capsys
):
    live = tmp_path / "live.db"
    restore_source = tmp_path / "restore_source.db"
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    create_database(live)
    with closing(sqlite3.connect(live)) as connection:
        connection.execute(
            "UPDATE student_records SET student_name = ?",
            ("Original Student",),
        )
        connection.commit()

    create_database(restore_source)
    with closing(sqlite3.connect(restore_source)) as connection:
        connection.execute(
            "UPDATE student_records SET student_name = ?",
            ("Restored Student",),
        )
        connection.commit()

    recovery.create_backup(restore_source, backup_dir)

    monkeypatch.setattr(recovery, "DATABASE_PATH", live)
    monkeypatch.setattr(recovery, "DEFAULT_BACKUP_DIR", backup_dir)
    monkeypatch.setattr(recovery, "server_appears_running", lambda: False)

    original_integrity_check = recovery.integrity_check

    def fail_after_restore(connection):
        original_integrity_check(connection)
        database_path = Path(
            connection.execute("PRAGMA database_list").fetchone()[2]
        )

        if database_path.resolve() == live.resolve():
            student = connection.execute(
                "SELECT student_name FROM student_records"
            ).fetchone()[0]

            if student == "Restored Student":
                raise RuntimeError(
                    "Simulated post-restore verification failure"
                )

    monkeypatch.setattr(recovery, "integrity_check", fail_after_restore)

    answers = iter(["1", "RESTORE"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    result = recovery.main()
    captured = capsys.readouterr()
    output = captured.out
    error_output = captured.err

    assert result == 1
    assert "Previous live database restored from rollback." in output, (
        f"STDOUT:\n{output}\nSTDERR:\n{error_output}"
    )
    assert "Simulated post-restore verification failure" in error_output

    assert_database_integrity(live)
    assert get_student_name(live) == "Original Student"

    failed_files = list(tmp_path.glob(".live_failed_*.db"))
    assert len(failed_files) == 1
    assert_database_integrity(failed_files[0])
    assert get_student_name(failed_files[0]) == "Restored Student"



def test_end_to_end_recovery_reports_rollback_failure(
    tmp_path, monkeypatch, capsys
):
    live = tmp_path / "live.db"
    restore_source = tmp_path / "restore_source.db"
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    create_database(live)
    with closing(sqlite3.connect(live)) as connection:
        connection.execute(
            "UPDATE student_records SET student_name = ?",
            ("Original Student",),
        )
        connection.commit()

    create_database(restore_source)
    with closing(sqlite3.connect(restore_source)) as connection:
        connection.execute(
            "UPDATE student_records SET student_name = ?",
            ("Restored Student",),
        )
        connection.commit()

    selected_backup = recovery.create_backup(restore_source, backup_dir)

    monkeypatch.setattr(recovery, "DATABASE_PATH", live)
    monkeypatch.setattr(recovery, "DEFAULT_BACKUP_DIR", backup_dir)
    monkeypatch.setattr(recovery, "server_appears_running", lambda: False)

    original_integrity_check = recovery.integrity_check

    def fail_after_restore(connection):
        original_integrity_check(connection)
        database_path = Path(
            connection.execute("PRAGMA database_list").fetchone()[2]
        )

        if database_path.resolve() == live.resolve():
            student = connection.execute(
                "SELECT student_name FROM student_records"
            ).fetchone()[0]

            if student == "Restored Student":
                raise RuntimeError(
                    "Simulated post-restore verification failure"
                )

    monkeypatch.setattr(recovery, "integrity_check", fail_after_restore)

    original_replace = recovery.os.replace

    def fail_rollback_replace(source, destination):
        source_path = Path(source)
        destination_path = Path(destination)

        if (
            source_path.name.startswith(".live_rollback_")
            and destination_path == live
        ):
            raise OSError("Simulated rollback replacement failure")

        return original_replace(source, destination)

    monkeypatch.setattr(recovery.os, "replace", fail_rollback_replace)

    answers = iter(["1", "RESTORE"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    result = recovery.main()
    captured = capsys.readouterr()
    output = captured.out
    error_output = captured.err

    assert result == 1
    assert "CRITICAL: Automatic rollback failed" in error_output
    assert "Simulated rollback replacement failure" in error_output
    assert "Simulated post-restore verification failure" in error_output

    rollback_files = list(tmp_path.glob(".live_rollback_*.db"))
    failed_files = list(tmp_path.glob(".live_failed_*.db"))

    assert len(rollback_files) == 1
    assert len(failed_files) == 1

    # The original database remains available in the rollback file.
    assert_database_integrity(rollback_files[0])
    assert get_student_name(rollback_files[0]) == "Original Student"

    # The failed restored database remains available for investigation.
    assert_database_integrity(failed_files[0])
    assert get_student_name(failed_files[0]) == "Restored Student"

    # The independent safety backup also preserves the original database.
    safety_backups = [
        path
        for path in backup_dir.glob("*.db")
        if path != selected_backup
    ]
    assert safety_backups
    assert any(
        get_student_name(path) == "Original Student"
        for path in safety_backups
    )

    # The live path may be absent because the simulated rollback failed.
    assert not live.exists()

def test_replace_live_database_swaps_sqlite_files(tmp_path):
    live = tmp_path / "live.db"
    staging = tmp_path / "staging.db"
    rollback = tmp_path / "rollback.db"

    create_database(live)
    create_database(staging)

    with closing(sqlite3.connect(live)) as connection:
        connection.execute(
            "UPDATE student_records SET student_name = ?",
            ("Original Student",),
        )
        connection.commit()

    with closing(sqlite3.connect(staging)) as connection:
        connection.execute(
            "UPDATE student_records SET student_name = ?",
            ("Restored Student",),
        )
        connection.commit()

    recovery.replace_live_database(staging, live, rollback)

    assert_database_integrity(live)
    assert_database_integrity(rollback)
    assert get_student_name(live) == "Restored Student"
    assert get_student_name(rollback) == "Original Student"
