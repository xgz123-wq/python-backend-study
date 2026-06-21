"""
数据模型（知识点5：SQLAlchemy 异步集成）
"""
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
