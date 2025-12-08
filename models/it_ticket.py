from services.database_manager import DatabaseManager
from pathlib import Path
import pandas as pd

class ITTicket:
    """Represents an IT Tickets in the platform"""

    #creating variables of the class
    def __init__(self, ticket_id: int, title: str, priority: str, status: str, assighned_to: str, db: DatabaseManager):
        self.__id = ticket_id
        self.__title = title
        self.__priority = priority
        self.__status = status
        self.__assigned_to = assighned_to
        self.__db = db

    def assign_to(self, staff: str) -> None:
        """Assigns self to a staff."""
        self.__assigned_to = staff

    def close_ticket(self) -> None:
        """Sets status of a ticket to close"""
        self.__status = "Closed"

    def get_status(self) -> str:
        """Returns a status of the ticket"""
        return self.__status
    
    #self description
    def __str__(self) -> str:
        return(
            f"Ticket {self.__id}: {self.__title} "
            f"[{self.__priority}] - {self.__status} (assigned to: {self.__assigned_to})"
        )
    
# =======================
# CRUD FUNCTIONS
# =======================

    #INSERT TICKET
    def insert_ticket(self, ticket_id: int, priority: str, status: str, category: str, subject: str, description: str, created_date: str, resolved_date: str | None, assigned_to: str, created_at: str) -> int:
        """Insert a new ticket into the database."""
        result = self.__db.execute_query(
            """
            INSERT INTO it_tickets
            (ticket_id, priority, status, category, subject, description,
             created_date, resolved_date, assigned_to, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_id,
                priority,
                status,
                category,
                subject,
                description,
                created_date,
                resolved_date,
                assigned_to,
                created_at,
            ),
        )
        return result.lastrowid
    
    #GET ALL TICKETS
    def get_all_tickets(self) -> pd.DataFrame:
        """Get all tickets as a DataFrame."""
        rows = self.__db.fetch_all(
            "SELECT * FROM it_tickets ORDER BY id DESC"
        )

        return pd.DataFrame(
            rows,
            columns=[
                "id",
                "ticket_id",
                "priority",
                "status",
                "category",
                "subject",
                "description",
                "created_date",
                "resolved_date",
                "assigned_to",
                "created_at",
            ],
        )
    
    #UPDATE STATUS
    def update_ticket_status(self, ticket_id: int, new_status: str) -> int:
        """Update the status of a ticket."""
        result = self.__db.execute_query(
            "UPDATE it_tickets SET status = ? WHERE id = ?",
            (new_status, ticket_id),
        )
        return result.rowcount

    #DELETE TICKET
    def delete_ticket(self, ticket_id: int) -> int:
        """Delete a ticket from the database."""
        result = self.__db.execute_query(
            "DELETE FROM it_tickets WHERE id = ?",
            (ticket_id,),
        )
        return result.rowcount
    
    #GET SORTED TICKETS BY CATEGORY COUNT
    def get_tickets_by_category_count(self) -> pd.DataFrame:
        query = """
        SELECT category, COUNT(*) as count
        FROM it_tickets
        GROUP BY category
        ORDER BY count DESC
        """
        rows = self.__db.fetch_all(query)
        return pd.DataFrame(rows, columns=["category", "count"])

    #GET TICKETS WITH STATUS
    def get_tickets_by_status(self, status: str = "Open") -> pd.DataFrame:
        rows = self.__db.fetch_all(
            "SELECT * FROM it_tickets WHERE status = ?", (status,)
        )

        return pd.DataFrame(
            rows,
            columns=[
                "id",
                "ticket_id",
                "priority",
                "status",
                "category",
                "subject",
                "description",
                "created_date",
                "resolved_date",
                "assigned_to",
                "created_at",
            ],
        )
    
    #MIGRATE CSV TICKETS TO DB
    def migrate_tickets(self) -> bool:
        """Migrates all tickets from CSV into the database."""
        BASE_DIR = Path(__file__).resolve().parent.parent
        DATA_DIR = BASE_DIR / "database"
        DB_PATH = DATA_DIR / "it_tickets.csv"

        df = pd.read_csv(DB_PATH)

        if df.empty:
            return False

        for _, row in df.iterrows():
            self.insert_ticket(
                ticket_id=row["ticket_id"],
                priority=row["priority"],
                status=row["status"],
                category=row["category"],
                subject=row["subject"],
                description=row["description"],
                created_date=str(row["created_date"]),
                resolved_date=str(row["resolved_date"])
                if not pd.isna(row["resolved_date"])
                else None,
                assigned_to=row["assigned_to"],
                created_at=str(row["created_at"]),
            )

        return True