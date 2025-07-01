from sqlalchemy import UniqueConstraint, VARCHAR
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.models.wb.base import Base
# Таблица shard_query
class ShardQueryTable(Base):
    __tablename__ = "shard_query"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR)
    shard: Mapped[str] = mapped_column(VARCHAR)
    query: Mapped[str] = mapped_column(VARCHAR)
    
    __table_args__ = (
        UniqueConstraint('shard', 'query', 'name', name='uix_shard_query_name'),
    )