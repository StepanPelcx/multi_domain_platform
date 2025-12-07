import bcrypt
from services.database_manager import DatabaseManager
class User:
    """Represents a user in the Multi-Domain Intelligence Platform."""

    def __init__(self, username: str, password_hash: str, role: str):
        self.__username = username
        self.__password_hash = password_hash
        self.__role = role

    def get_username(self) -> str:
        return self.__username
    
    def get_role(self) -> str:
        return self.__role
    
    #CHECKING PASSWORD
    def verify_password(self, plain_text_password: str) -> bool:
        """Returns True, if passwords match and False, if not."""
        # bcrypt.checkpw returns True if password matches, False otherwise
        return bcrypt.checkpw(
            plain_text_password.encode("utf-8"),
            self.__password_hash.encode("utf-8")
        )
    
    def __str__(self) -> str:
        return f"User({self.__username}, role={self.__role})"
