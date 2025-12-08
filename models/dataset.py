from services.database_manager import DatabaseManager
from datetime import date
import pandas as pd
from pathlib import Path

class Dataset:
    """Represents a data science dataset in the platform."""

    #creating variables of the class
    def __init__(self, dataset_id: int, name: str, size_bytes: int, rows: int, source: str, db: DatabaseManager):
        self.__id = dataset_id
        self.__name = name
        self.__size_bytes = size_bytes
        self.__rows = rows
        self.__source = source
        self.__db = db

    def calculate_size_mb(self) -> float:
        """Returns calculated size in mega bytes."""
        return self.__size_bytes / (1024 * 1024)
    
    def get_source(self) -> str:
        """Returns a source of the dataset."""
        return self.__source
    
    #self description
    def __str__(self) -> str:
        size_mb = self.calculate_size_mb()
        return f"Dataset {self.__id}: {self.__name} ({size_mb:.2f} MB, {self.__rows} rows)"
    
# =======================
# CRUD FUNCTIONS
# =======================

    #INSERT DATASET   
    def insert_dataset(self, dataset_name, category, source, last_updated, record_count, file_size_mb, created_at):
        """Insert a new dataset into the database."""
        cur = self.__db.execute_query(
            """
            INSERT INTO datasets_metadata
            (dataset_name, category, source, last_updated, record_count, file_size_mb, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (dataset_name, category, source, last_updated, record_count, file_size_mb, created_at)
        )
        return cur.lastrowid

    #GET ALL DATASETS
    def get_all_datasets(self):
        """Get all incidents as DataFrame."""
        rows = self.__db.fetch_all(
            "SELECT * FROM datasets_metadata ORDER BY id DESC"
        )

        return pd.DataFrame(
            rows,
            columns=[
                "id",
                "dataset_name",
                "category",
                "source",
                "last_updated",
                "record_count",
                "file_size_mb",
                "created_at"
            ]
        )

    #UPDATE RECORD COUNT
    def update_dataset_record_count(self, dataset_id, new_record_count):
        """Update the record count of a dataset."""
        last_updated = date.today()
        cur = self.__db.execute_query(
            """
            UPDATE datasets_metadata
            SET record_count = ?, last_updated = ?
            WHERE id = ?
            """,
            (new_record_count, last_updated, dataset_id)
        )
        return cur.rowcount

    #DELETE DATASET
    def delete_dataset(self, dataset_id):
        """Delete a dataset from the database."""
        cur = self.__db.execute_query(
            "DELETE FROM datasets_metadata WHERE id = ?",
            (dataset_id,)
        )
        return cur.rowcount

    #GET DATASETS BY CATEGORY COUNT
    def get_datasets_by_category_count(self):
        """Returns a df grouped by category."""
        rows = self.__db.fetch_all(
            """
            SELECT category, COUNT(*) AS count
            FROM datasets_metadata
            GROUP BY category
            ORDER BY count DESC
            """
        )

        # Convert to DataFrame
        return pd.DataFrame(rows, columns=["category", "count"])

    #GET REPEATING DATASET CATEGORIES
    def get_repeating_dataset_categories(self, min_count=5):
        """Returns a df with categories with more then X samples."""
        rows = self.__db.fetch_all(
            """
            SELECT category, COUNT(*) AS count
            FROM datasets_metadata
            GROUP BY category
            HAVING COUNT(*) > ?
            ORDER BY count DESC
            """,
            (min_count,)
        )

        # Convert to DataFrame
        return pd.DataFrame(rows, columns=["category", "count"])

    #MIGRATE CSV DATASETS TO DB
    def migrate_datasets(self):
        """Migrates all datasets info from the CSV file."""
        #getting the path
        BASE_DIR = Path(__file__).resolve().parent.parent
        DATA_DIR = BASE_DIR / "database"
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        DB_PATH = DATA_DIR / "datasets_metadata.csv"

        df = pd.read_csv(DB_PATH)

        if not df.empty:
            for index, row in df.iterrows():
                Dataset.insert_dataset(
                    self,
                    dataset_name=row["dataset_name"],
                    category=row["category"],
                    source=row["source"],
                    last_updated=str(row["last_updated"]),
                    record_count=int(row["record_count"]),
                    file_size_mb=float(row["file_size_mb"]),
                    created_at=str(row["created_at"])
                )
            return True
        return False