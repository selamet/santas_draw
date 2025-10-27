"""
User model
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from app.models.base import BaseModel

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    """User model with email and password"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash"""
        return pwd_context.verify(password, self.password)
