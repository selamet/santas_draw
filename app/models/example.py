"""
Example model demonstrating BaseModel usage
"""

from sqlalchemy import Column, Integer, String
from app.models.base import BaseModel


class ExampleModel(BaseModel):
    """Example model showing how to use BaseModel"""
    
    __tablename__ = "examples"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    
    # created_at and updated_at are automatically inherited from BaseModel
