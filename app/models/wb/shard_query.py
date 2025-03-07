from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import registry

mapper_registry = registry()

# Таблица shard_query
class ShardQueryTable:
    __tablename__ = 'shard_query'
    id = Column(Integer, primary_key=True)
    name = Column(String(500))
    shard = Column(String(500))
    query = Column(String(500))
