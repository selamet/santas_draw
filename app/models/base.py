"""
Base model with common fields
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from app.models.database import Base


class TimestampMixin:
    """Mixin class for created_at and updated_at timestamps"""
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False
        )


class BaseModel(Base, TimestampMixin):
    """Base model class with common fields"""
    
    __abstract__ = True
    
    def __repr__(self):
        """String representation of the model"""
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', 'N/A')})>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
