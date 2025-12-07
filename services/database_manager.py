import sqlite3
from typing import Any, Iterable
from pathlib import Path

class DatabaseManager:
    """Handles SQLite database connections and queries."""

    def __init__(self):
        #CONNECTING FUNCTION
        BASE_DIR = Path(__file__).resolve().parent.parent
        DATA_DIR = BASE_DIR / "database"
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        DB_PATH = DATA_DIR / "intelligent_platform.db"

        self.__db_path = DB_PATH
        self.__connection: sqlite3.Connection | None = None

    #CONNECT
    def connect(self) -> None:
        if self.__connection is None:
            self.__connection = sqlite3.connect(self.__db_path)

    #CLOSE CONNECTION
    def close(self) -> None:
        if self.__connection is not None:
            self.__connection.close()
            self.__connection = None

    #EXECUTE QUERY
    def execute_query(self, sql: str, params: Iterable[Any] = ()):
        """Execute a write query (INSERT, UPDATE, DELETE)."""
        if self.__connection is None:
            self.connect()
        cur = self.__connection.cursor()
        cur.execute(sql, tuple(params))
        self.__connection.commit()
        return cur
    
    #FETCH ONE
    def fetch_one(self, sql: str, params: Iterable[Any] = ()):
        if self.__connection is None:
            self.connect()
        cur = self.__connection.cursor()
        cur.execute(sql, tuple(params))
        return cur.fetchone()
    
    #FETCH ALL
    def fetch_all(self, sql: str, params: Iterable[Any] = ()):
        if self.__connection is None:
            self.connect()
        cur = self.__connection.cursor()
        cur.execute(sql, tuple(params))
        return cur.fetchall()
    
    #CREATING USERS TABLE
    def create_users_table(self):
        """Creates users table, if not already created."""
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            )
        """)
        print("✅ Users table created successfully!")

    #CREATING INCIDENTS TABLE
    def create_cyber_incidents_table(self):
        """Creates incidents table, if not already created."""
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS cyber_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                incident_type TEXT,
                severity TEXT,
                status TEXT,
                description TEXT,
                reported_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Cyber incidents table created successfully!")

    #CREATING DATASETS TABLE
    def create_datasets_metadata_table(self):
        """Creates datasets table, if not already created."""
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS datasets_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_name TEXT NOT NULL,
                category TEXT,
                source TEXT,
                last_updated TEXT,
                record_count INTEGER,
                file_size_mb REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Datasets metadata table created successfully!")

    #CREATING TICKETS TABLE
    def create_it_tickets_table(self):
        """Creates tickets table, if not already created."""
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS it_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT UNIQUE NOT NULL,
                priority TEXT,
                status TEXT,
                category TEXT,
                subject TEXT NOT NULL,
                description TEXT,
                created_date TEXT,
                resolved_date TEXT,
                assigned_to TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ IT tickets table created successfully!")

    #CREATING ALL TABLES
    def create_all_tables(self):
        """Creates all tables, if they are not already created."""
        self.create_users_table()
        self.create_cyber_incidents_table()
        self.create_datasets_metadata_table()
        self.create_it_tickets_table()
        print("✅ All tables created successfully!")