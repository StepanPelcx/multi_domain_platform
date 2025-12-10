import bcrypt
from services.database_manager import DatabaseManager
class User:
    """Represents a user in the Multi-Domain Intelligence Platform."""

    def __init__(self, username: str, password_hash: str, role: str, db: DatabaseManager = DatabaseManager()):
        self.__username = username
        self.__password_hash = password_hash
        self.__role = role
        self.__db = DatabaseManager()

    def get_username(self) -> str:
        return self.__username
    
    def get_role(self, username: str):
        """
        Returns the role of a user using the username.
        Returns None if the username does not exist.
        """
        row = self.__db.fetch_one(
            "SELECT role FROM users WHERE username = ?", (username,)
        )
        if row:
            return row[0]  # the role
        return None
    
    #CHECKING PASSWORD
    def verify_password(self, username: str, plain_text_password: str) -> bool:
        """Verify password by fetching hash from database using username."""
        
        #Get stored password hash from DB
        row = self.__db.fetch_one(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,)
        )
        #checking if user does not exist
        if row is None:
            return False

        stored_hash = row[0]

        #Comparing passwords using bcrypt
        return bcrypt.checkpw(
            plain_text_password.encode("utf-8"),
            stored_hash.encode("utf-8")
        )
    
    def __str__(self) -> str:
        return f"User({self.__username}, role={self.__role})"
