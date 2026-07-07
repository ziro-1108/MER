from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class PptJob(Base):
    __tablename__ = "ppt_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_number: Mapped[str] = mapped_column(String(120), index=True)
    sample_number: Mapped[str] = mapped_column(String(120), index=True)
    combined_key: Mapped[str] = mapped_column(String(260), index=True)
    status: Mapped[str] = mapped_column(String(40), default="processing", index=True)
    image_count: Mapped[int] = mapped_column(Integer, default=0)
    pptx_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    xlsx_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_xlsx_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
