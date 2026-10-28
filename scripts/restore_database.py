
"""Interactively restore an EduAnalytics backup to the live SQLite database."""

import os
import socket
import sqlite3
import sys
import uuid
from datetime import datetime
from pathlib import Path

try:
    from scripts.backup_database import (
        DATABASE_PATH,
        DEFAULT_BACKUP_DIR,
        METADATA_TABLE,
        create_backup,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from backup_database import (
        DATABASE_PATH,
        DEFAULT_BACKUP_DIR,
        METADATA_TABLE,
        create_backup,
    )


def integrity_check(connection: sqlite3.Connection) -> None:
    result = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if result != "ok":
        raise RuntimeError(f"Integrity check failed: {result}")


def institution_name(connection: sqlite3.Connection) -> str:
    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    if "institution" not in tables:
        raise RuntimeError("Missing institution table.")

    rows = connection.execute(
        "SELECT name FROM institution ORDER BY id"
    ).fetchall()
    if len(rows) != 1 or not rows[0][0].strip():
        raise RuntimeError("Expected exactly one named institution.")
    return rows[0][0].strip()


def inspect_backup(path: Path) -> dict:
    """Validate a backup and read its institution and timestamp."""
    uri = path.resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    try:
        integrity_check(connection)
        name = institution_name(connection)
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

        timestamp = None
        if METADATA_TABLE in tables:
            metadata = connection.execute(
                f'SELECT institution_name, created_at, format_version '
                f'FROM "{METADATA_TABLE}" WHERE id = 1'
            ).fetchone()
            if not metadata or metadata[2] != 1:
                raise RuntimeError("Invalid backup metadata.")
            if metadata[0] != name:
                raise RuntimeError("Backup metadata institution mismatch.")
            timestamp = metadata[1]
    finally:
        connection.close()

    if timestamp is None:
        timestamp = datetime.fromtimestamp(
            path.stat().st_mtime
        ).astimezone().isoformat(timespec="seconds")

    return {
        "path": path,
        "institution": name,
        "timestamp": timestamp,
    }


def prepare_restored_database(backup: Path, staging: Path) -> None:
    """Prepare and validate a replacement database without touching live DB."""
    source_uri = backup.resolve().as_uri() + "?mode=ro"
    source = sqlite3.connect(source_uri, uri=True)
    try:
        integrity_check(source)
        institution_name(source)

        target = sqlite3.connect(str(staging), timeout=30)
        try:
            source.backup(target)

            # Backup metadata belongs in backup files, not the live database.
            target.execute(f'DROP TABLE IF EXISTS "{METADATA_TABLE}"')
            target.commit()
            integrity_check(target)
            institution_name(target)
        finally:
            target.close()
    finally:
        source.close()

def server_appears_running() -> bool:
    """Conservatively check the managed PID file and default web port."""
    project_root = DATABASE_PATH.parent.parent
    pid_file = project_root / ".eduanalytics.pid"

    if pid_file.exists():
        return True

    try:
        with socket.create_connection(("127.0.0.1", 5000), timeout=1):
            return True
    except OSError:
        return False

def replace_live_database(staging: Path, live: Path, rollback: Path) -> None:
    """Replace the database with a rollback path if the file swap fails."""
    os.replace(live, rollback)
    try:
        os.replace(staging, live)
    except Exception:
        os.replace(rollback, live)
        raise

def main() -> int:
    if not DATABASE_PATH.is_file():
        print(f"ERROR: Live database not found: {DATABASE_PATH}", file=sys.stderr)
        return 1

    if server_appears_running():
        print(
            "ERROR: EduAnalytics may be running. Stop it with .\\stop.ps1, "
            "close other processes that may access the database, and retry.",
            file=sys.stderr,
        )
        return 1

    if not DEFAULT_BACKUP_DIR.is_dir():
        print(f"No backup folder found: {DEFAULT_BACKUP_DIR}")
        return 1

    try:
        live_db = sqlite3.connect(str(DATABASE_PATH), timeout=10)
        try:
            live_institution = institution_name(live_db)
            integrity_check(live_db)
        finally:
            live_db.close()

        backups = []
        print("\nEduAnalytics - Database Recovery")
        print(f"Institution: {live_institution}")
        print("\nAvailable backups:")

        for path in sorted(
            DEFAULT_BACKUP_DIR.glob("*.db"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        ):
            try:
                item = inspect_backup(path)
                if item["institution"] != live_institution:
                    print(f"  [SKIP] {path.name} - different institution")
                    continue
                backups.append(item)
            except (sqlite3.Error, OSError, RuntimeError, ValueError) as exc:
                print(f"  [SKIP] {path.name} - invalid backup ({exc})")

        if not backups:
            print("No valid backups for this institution were found.")
            return 1

        for index, item in enumerate(backups, start=1):
            try:
                readable_time = datetime.fromisoformat(
                    item["timestamp"]
                ).astimezone().strftime("%d %B %Y, %I:%M:%S %p")
            except ValueError:
                readable_time = item["timestamp"]

            print(f"\n[{index}] {item['institution']}")
            print(f"    Date: {readable_time}")
            print(f"    File: {item['path'].name}")

        choice = input("\nEnter backup number (or Q to cancel): ").strip()
        if choice.lower() == "q":
            print("Recovery cancelled. No changes made.")
            return 0
        if not choice.isdigit() or not 1 <= int(choice) <= len(backups):
            print("ERROR: Invalid selection.", file=sys.stderr)
            return 1

        selected = backups[int(choice) - 1]
        print(f"\nSelected: {selected['path'].name}")
        print("WARNING: The current live database will be replaced.")
        print("A safety backup will be created first.")
        if input("Type RESTORE to continue: ").strip() != "RESTORE":
            print("Recovery cancelled. No changes made.")
            return 0

        # Recheck after user interaction, before preparing the replacement.
        if server_appears_running():
            raise RuntimeError(
                "The server appears to be running. No recovery was performed."
            )

        staging = DATABASE_PATH.with_name(
            f".{DATABASE_PATH.stem}_restore_{uuid.uuid4().hex}.db"
        )
        rollback = DATABASE_PATH.with_name(
            f".{DATABASE_PATH.stem}_rollback_{uuid.uuid4().hex}.db"
        )

        print("\nCreating safety backup...")
        safety_backup = create_backup(DATABASE_PATH, DEFAULT_BACKUP_DIR)
        print(f"Safety backup: {safety_backup.name}")

        try:
            print("Preparing and validating selected backup...")
            prepare_restored_database(selected["path"], staging)

            # Refuse if sidecar files suggest an active or unfinished SQLite
            # WAL session; do not delete these files automatically.
            for suffix in ("-wal", "-shm"):
                if Path(str(DATABASE_PATH) + suffix).exists():
                    raise RuntimeError(
                        f"SQLite sidecar file exists: {DATABASE_PATH}{suffix}. "
                        "Investigate it before recovery."
                    )

            if server_appears_running():
                raise RuntimeError(
                    "The server appears to be running. Live database unchanged."
                )

            print("Replacing live database...")
            replace_live_database(staging, DATABASE_PATH, rollback)

            restored = sqlite3.connect(str(DATABASE_PATH), timeout=10)
            try:
                integrity_check(restored)
                restored_institution = institution_name(restored)
            finally:
                restored.close()

            if restored_institution != live_institution:
                raise RuntimeError("Restored institution verification failed.")

            print("\nRecovery completed successfully.")
            print(f"Institution: {restored_institution}")
            print(f"Restored from: {selected['path'].name}")
            print("Integrity: Verified")
            print(f"Safety backup: {safety_backup}")
            print(f"Previous live database retained at: {rollback}")
            print("Restart EduAnalytics with .\\start.ps1.")
            return 0

        except Exception:
            # If replacement happened but final verification failed, restore
            # the previous database from the retained rollback file.
            if rollback.exists():
                try:
                    failed_live = DATABASE_PATH.with_name(
                        f".{DATABASE_PATH.stem}_failed_{uuid.uuid4().hex}.db"
                    )
                    if DATABASE_PATH.exists():
                        os.replace(DATABASE_PATH, failed_live)
                    os.replace(rollback, DATABASE_PATH)
                    print("Previous live database restored from rollback.")
                except OSError as rollback_error:
                    print(
                        f"CRITICAL: Automatic rollback failed: {rollback_error}",
                        file=sys.stderr,
                    )
                    print(f"Safety backup: {safety_backup}", file=sys.stderr)
                    print(f"Rollback file: {rollback}", file=sys.stderr)
            raise
        finally:
            if staging.exists():
                staging.unlink()

    except (sqlite3.Error, OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: Recovery failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
