import bcrypt
from typing import Optional
from models.user import User
from services.database_manager import DatabaseManager



class Hasher:
    """Hasher functions for registering the user."""

    def hash_password(plain_text_password: str) -> str:
        """Returns a hashed password, created from plain text password."""
        #Encoding plain password into bytes
        password_bytes = plain_text_password.encode('utf-8')
        #generating salt
        salt = bcrypt.gensalt()
        #adding salt to the password
        __hashed_password = bcrypt.hashpw(password_bytes, salt)
        #Decoding the password
        __hashed_str = __hashed_password.decode('utf-8')
        return __hashed_str
        
    def check_password(plain_text_password: str, hashed: str) -> bool:
        """Returns if the hashed password match or not."""
        return Hasher.hash_password(plain_text_password) == hashed
        
    
class AuthManager:
    """Handles user registration and login."""

    def __init__(self, db: DatabaseManager):
        self._db = db

    def register_user(self, username: str, password: str, role: str = "user"):
        password_hash = Hasher.hash_password(password)
        self._db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)"
            (username, password_hash, role),
        )

    def login_user(self, username: str, password: str) -> Optional[User]:
        row = self._db.fetch_one(
            "SELECT username, password_hash, role FROM users WHERE username = ?"
            (username,),
        )
        if row is None:
            return None

        username_db, password_hash_db, role_db = row
        if Hasher.check_password(password, password_hash_db):
            return User(username_db, password_hash_db, role_db)
        return None