from sqlalchemy import String, DateTime, Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    input = Column(String, nullable=False)

    output = Column(JSONB, nullable=True)
