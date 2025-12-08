from services.database_manager import DatabaseManager
from pathlib import Path
import pandas as pd

class SecurityIncident:
    """Represents a cybersecurity incident in the platform."""

    #creating variables of the class
    def __init__(self, incident_id: int, incident_type: str, severity: str, status: str, description: str, reported_by: str, db: DatabaseManager):
        self.__id = incident_id
        self.__incident_type = incident_type
        self.__severity = severity
        self.__status = status
        self.__description = description
        self.__reported_by = reported_by
        self.__db = db

    def get_id(self) -> str:
        """Returns id of the incident."""
        return self.__id
    
    def get_severity(self) -> str:
        """Returns severity of the incident."""
        return self.__severity
    
    def get_status(self) -> str:
        """Returns status of the incident."""
        return self.__status
    
    def get_description(self) -> str:
        """Returns description of the incident."""
        return self.__description
    
    def update_status(self, new_status: str) -> None:
        """Updates status of the incident."""
        self.__status = new_status

    def get_severity_level(self) -> int:
        """Return an integer severity level."""
        mapping = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }
        return mapping.get(self.__severity.lower(), 0)
    
    #self description
    def __str__(self) -> str:
        return f"Incident {self.__id} [{self.__severity.upper()}] {self.__incident_type}"
    
# =======================
# CRUD FUNCTIONS
# =======================

    #INSERT INCIDENT
    def insert_incident(self, date: str, incident_type: str, severity: str, status: str, description: str, reported_by: str | None = None,) -> int:
        """Insert a new cyber incident into the database."""
        result = self.__db.execute_query(
            """
            INSERT INTO cyber_incidents
            (date, incident_type, severity, status, description, reported_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (date, incident_type, severity, status, description, reported_by),
        )
        return result.lastrowid
    
    #UPDATE INCIDENT
    def update_incident_status(self, incident_id: int, new_status: str) -> int:
        """Update the status of an incident."""
        result = self.__db.execute_query(
            "UPDATE cyber_incidents SET status = ? WHERE id = ?",
            (new_status, incident_id),
        )
        return result.rowcount
    
    #DELETE INCIDENT
    def delete_incident(self, incident_id: int) -> int:
        """Delete an incident."""
        result = self.__db.execute_query(
            "DELETE FROM cyber_incidents WHERE id = ?",
            (incident_id,),
        )
        return result.rowcount
    
    #GET INCIDENT BY TYPE COUNT
    def get_incidents_by_type_count(self) -> pd.DataFrame:
        query = """
        SELECT incident_type, COUNT(*) AS count
        FROM cyber_incidents
        GROUP BY incident_type
        ORDER BY count DESC
        """
        rows = self.__db.fetch_all(query)
        return pd.DataFrame(rows, columns=["incident_type", "count"])
    
    #GET INCIDENTS WITH HIGH SEVERITY STATUS
    def get_high_severity_by_status(self) -> pd.DataFrame:
        query = """
        SELECT status, COUNT(*) AS count
        FROM cyber_incidents
        WHERE severity = 'High'
        GROUP BY status
        ORDER BY count DESC
        """
        rows = self.__db.fetch_all(query)
        return pd.DataFrame(rows, columns=["status", "count"])
    
    #GET INCIDENTS WITH MANY CASES
    def get_incident_types_with_many_cases(self, min_count: int = 5) -> pd.DataFrame:
        query = """
        SELECT incident_type, COUNT(*) AS count
        FROM cyber_incidents
        GROUP BY incident_type
        HAVING COUNT(*) > ?
        ORDER BY count DESC
        """
        rows = self.__db.fetch_all(query, (min_count,))
        return pd.DataFrame(rows, columns=["incident_type", "count"])

    #MIGRATE CSV FILE INTO DB
    def migrate_incidents(self) -> bool:
        """Migrates all incidents from CSV file into the database."""
        BASE_DIR = Path(__file__).resolve().parent.parent
        DATA_DIR = BASE_DIR / "database"
        DB_PATH = DATA_DIR / "cyber_incidents.csv"

        df = pd.read_csv(DB_PATH)
 
        if df.empty:
            return False
        #migration loop
        for item, row in df.iterrows():
            self.insert_incident(
                date=str(row["date"]),
                incident_type=row["incident_type"],
                severity=row["severity"],
                status=row["status"],
                description=row["description"],
                reported_by=row.get("reported_by"),
            )
        return True
    
    