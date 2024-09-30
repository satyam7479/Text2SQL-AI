from sqlalchemy import Column, INTEGER, String, TIMESTAMP, text, ForeignKey,TEXT, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from config.database import Base
from sqlalchemy.dialects.mysql import LONGTEXT
import os

class AskllmLogsModel(Base):
    __tablename__ = os.getenv("DB_PREFIX")+"askllm_logs"
    id = Column(INTEGER, primary_key=True,index=True)
    question=Column(TEXT)
    master_id=Column(INTEGER, nullable=True)
    query=Column(LONGTEXT,nullable=True)
    active=Column(Boolean,nullable=True)
    ip_address=Column(String(100),nullable=True)
    created_on=Column(TIMESTAMP, nullable=False,
                        server_default=text("CURRENT_TIMESTAMP"))
    created_by_id=Column(INTEGER)
    store_id = Column(INTEGER)