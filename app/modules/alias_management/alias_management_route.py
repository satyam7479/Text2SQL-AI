from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.modules.alias_management.alias_management_serevice import ListAliasesService
from config.database import getDb, msg
from app.dto import  response_schema

load_dotenv(verbose=True)

router = APIRouter(prefix="/api", tags=["Alias"])

# Get search history of asked questions 
@router.get("/list/aliases", summary="Retrieve Aliases for seting Visibility, Priority and Column Mappings")
def listAliases(db: Session = Depends(getDb)):
    all_responses=ListAliasesService.listAliases(db=db)
    if all_responses is not None:
        return response_schema.ResponseSchema(response=msg["search_questions"], data=all_responses)
    else:
        return response_schema.ResponseSchema(status=False,response=msg["no_record_found"], data=None)