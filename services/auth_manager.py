import bcrypt
import re
import pandas as pd
from typing import Optional
from models.user import User
from services.database_manager import DatabaseManager
import secrets



class Hasher:
    """Hasher functions for registering the user."""

    def __init__(self, db: DatabaseManager):
        self.__db = db
    #HASH PASSWORD
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
    
    #CHANGE PASSWORD
    def change_password(self, username: str, new_password: str) -> bool:
        """Changes the password of a user."""
        new_hashed = self.hash_password(new_password)
        rows_updated = self.__db.execute_query(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (new_hashed, username)
        ).rowcount
        return rows_updated == 1
        
class AuthManager:
    """Handles user registration and login."""

    def __init__(self, db: DatabaseManager):
        self.__db = db


    #FINDING USER IN DATABASE
    def get_user_by_username(self, username: str):
        """Retrieve user by username."""
        row = self.__db.fetch_one("SELECT username, password_hash, role FROM users WHERE username = ?", (username,))
        if row:
            return User(*row)
        return None
    
    #ADDING USER TO THE DATABASE
    def insert_user(self, username: str, password_hash: str, role: str):
        """Insert new user."""
        self.__db.execute_query(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
        
    #VALIDATE USERNAME
    def validate_username(self, username: str) -> bool:
        return 3 <= len(username) <= 20 and username.isalnum()
    
    #VALIDATE PASSWORD
    def validate_password(self, password: str) -> bool:
        return (
            8 <= len(password) < 24
            and re.search(r"[A-Z]", password)
            and re.search(r"[a-z]", password)
            and re.search(r"\d", password)
            and re.search(r"[!@#$%^&*(),.?/\"':{}|<>]", password)
        )

    #REGISTER USER
    def register_user(self, username: str, password: str, role: str):
        """Returns if the user has been registered."""
        #Checking if the username already exists
        if self.get_user_by_username(username):
            return False
        #validating user credentials
        if not self.validate_username(username):
            return "username"
        if not self.validate_password(password):
            return "password"
        #Hashing the password
        hashed_str = Hasher.hash_password(password)
        #inserting user into database
        self.insert_user(username, hashed_str, role)
        return True
    

    #LOGIN USER
    def login_user(self, username: str, password: str) -> Optional[User]:
        #getting the user info
        user = self.get_user_by_username(username)
        if not user:
            return "username"
        if not user.verify_password(username=username, plain_text_password=password):
            return False
        return True
        
    #GET ALL USERS
    def get_all_users(self) -> pd.DataFrame:
        """Returns all users as a DataFrame."""
        rows = self.__db.fetch_all("SELECT username, role FROM users ORDER BY id DESC")
        return pd.DataFrame(rows, columns=["username", "role"])

    #CREATING TOKEN
    def create_session(self, username: str) -> str:
        """Creates a session token for the user."""
        token = secrets.token_hex(16)
        #storing token in DB for session management
        return token
    
    def check_password_strength(self, password):
        """Returns how strong the password is(weak, medium, strong)."""
        # Implement logic based on:
        # creating variable to store score for password strenght
        score = 0
        # - Length
        # checking length
        if len(password) > 16:
            if len(password) > 20:
                score += 10
            else:
                score += 5

        # creating variables for checking what characters are in the password
        numb = 0
        sc = 0
        ul = 0
        # - Presence of uppercase, lowercase, digits, special characters
        # counting how many of each characters are in the password
        for digit in password:
            if digit.isdigit():
                numb += 1
            if digit.isupper():
                ul += 1
            if not digit.isalnum():
                sc += 1

        # adding to score based on each character variable value
        if numb > 2:
            score += 10
        if sc > 1:
            score += 10
        if ul > 2:
            score += 10

    # - Common password patterns
        common_passwords = [
            "Password1!",
            "Welcome123!",
            "Admin@123",
            "Qwerty123!",
            "Summer2024!",
            "Winter2023@",
            "HelloWorld1!",
            "Test@1234",
            "ILoveYou2!",
            "Sunshine@9",
            "Abc12345!",
            "Football2025#",
            "London2024$",
            "Chocolate1!",
            "MyPass@123",
            "Secure123#",
            "HappyDay7@",
            "Dragon99!",
            "Freedom#22",
            "Monkey@88",
            "StarLight7!",
            "Galaxy2025!",
            "BlueSky@11",
            "Rainbow#123"
        ]

        # checking if password match one of the most common ones
        for item in common_passwords:
            if password == item:
                return "Your password is one of the most used. Try another."

        if score >= 25:
            return "Strong password"
        elif score >= 10:
            return "Medium password"
        else:
            return "Weak password"