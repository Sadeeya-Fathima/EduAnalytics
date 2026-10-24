import sqlite3

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()
login_manager = LoginManager()

@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(connection, connection_record):
    """Enable foreign-key enforcement for every SQLite connection."""
    if isinstance(connection, sqlite3.Connection):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()