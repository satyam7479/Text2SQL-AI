from sqlalchemy import create_engine, DateTime
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_easy_softdelete.mixin import generate_soft_delete_mixin_class
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import json
import os

load_dotenv(verbose=True)

# MSSQL_URL = "mssql+pymssql://"+os.getenv("DB_USERNAME")+":"+os.getenv("DB_PASSWORD")+"@"+os.getenv("DB_HOST")+":"+os.getenv("DB_PORT")+"/"+os.getenv("DB_DATABASE")
MYSQL_URL = "mysql+pymysql://"+os.getenv("DB_USERNAME")+":"+os.getenv("DB_PASSWORD")+"@"+os.getenv("DB_HOST")+"/"+os.getenv("DB_DATABASE")
POOL_SIZE = 20
POOL_RECYCLE = 3600
POOL_TIMEOUT = 15
MAX_OVERFLOW = 2
CONNECT_TIMEOUT = 60

# engine = create_engine(MSSQL_URL, pool_size=POOL_SIZE, pool_recycle=POOL_RECYCLE, pool_timeout=POOL_TIMEOUT, max_overflow=MAX_OVERFLOW)
engine = create_engine(MYSQL_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

file = open(os.getcwd() + '/response_msg.json')
msg = json.load(file)


# Create a Class that inherits from our class builder
class SoftDeleteMixin(generate_soft_delete_mixin_class()):
    # type hint for autocomplete IDE support
    deleted_at:DateTime

def getDb():
    db = SessionLocal()
    try:
        yield db
    except Exception as ex:
        print("Error getting DB session : ", ex)
        raise 
    finally:
        db.close()

def response(status, message, data):
    return {
        "status": status,
        "message": message,
        "data": data,
    }
