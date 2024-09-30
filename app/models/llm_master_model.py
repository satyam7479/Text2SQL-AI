from sqlalchemy import Column, INTEGER, String, TIMESTAMP, text,TEXT, Boolean
from config.database import Base , SoftDeleteMixin
from sqlalchemy.dialects.mysql import LONGTEXT
import os

class QueriesMaster(Base, SoftDeleteMixin):
    __tablename__ = os.getenv("DB_PREFIX")+"master_queries"
    id = Column(INTEGER, primary_key=True,index=True)
    questions=Column(TEXT,nullable=True)
    query=Column(LONGTEXT,nullable=True)
    columns_to_view=Column(TEXT, nullable=True)
    role_type=Column(String(50),nullable=True)
    added_by=Column(String(100),nullable=True)
    active=Column(Boolean,nullable=True)
    created_on=Column(TIMESTAMP, nullable=False,
                        server_default=text("CURRENT_TIMESTAMP"))
    updated_on = Column(TIMESTAMP, nullable=True,
                        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    deleted_at = Column(TIMESTAMP, nullable=True,server_default=text("NULL"))
    
