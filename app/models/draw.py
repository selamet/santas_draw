import datetime

from enum import Enum
from app.models.base import BaseModel
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean


class DrawType(str, Enum):
    ANONYMOUS = "anonymous"
    USER_CREATED = "user_created"


class DrawStatus(str, Enum):
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Draw(BaseModel):
    """Draw model representing a gift exchange event."""

    __tablename__ = "draws"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    creator = relationship("User", backref="created_draws", foreign_keys=[creator_id], passive_deletes=True)
    status = Column(String(50), default=DrawStatus.ACTIVE.value, nullable=False)
    draw_type = Column(String(50), default=DrawType.ANONYMOUS.value, nullable=False)
    draw_date = Column(DateTime(timezone=True), nullable=True)
    require_address = Column(Boolean(False), default=False)
    require_phone = Column(Boolean(False), default=False)
    share_link = Column(String(255), unique=True, nullable=True, index=True)

    @property
    def is_active(self) -> bool:
        return self.status == DrawStatus.ACTIVE.value and (
                self.draw_date and self.draw_date > datetime.datetime.now(datetime.UTC)
        )

    def __repr__(self):
        return f"<Draw(id={self.id}, name={self.name}, organizer_id={self.organizer_id})>"
