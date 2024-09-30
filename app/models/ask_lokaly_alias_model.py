from sqlalchemy import Column, INTEGER, String, Boolean
from config.database import Base , SoftDeleteMixin
import os

class AskLokalyAlias(Base):
    __tablename__ = os.getenv("DB_PREFIX")+"ask_lokaly_alias"
    alias_id = Column(INTEGER, primary_key=True, autoincrement=True)
    table_name = Column(String(255), nullable=False)
    column_name = Column(String(255), nullable=False)
    alias_name = Column(String(255), nullable=True, default=None)
    sequence = Column(INTEGER, nullable=False)
    is_included=Column(Boolean,nullable=True)

