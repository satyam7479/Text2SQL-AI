# ask_llm_log_route file to manage AI and it's responses

from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, Depends, Form, Request
from sqlalchemy.orm import Session
from app.helper.general_helper import Helper
from app.helper.vanna_helper import Helper as vn_helper
from config.database import getDb, msg
from typing import Optional
from fastapi_pagination import Params
from app.dto import  response_schema
from app.modules.ask_llm.ask_llm_log_service import AskLLMLogService

load_dotenv(verbose=True)

router = APIRouter(prefix="/api", tags=["Questions"])

# Ask questions
@router.post("/ask/questions/{created_by_id}", summary="Ask questions")
def askQuestion(request: Request, background_tasks: BackgroundTasks, created_by_id: int ,store_id:  int = Form(None),question_id: int = Form(None), question: str = Form(None),contexts: str = Form(None),role_type:  str = Form(),
                   db: Session = Depends(getDb),search_string:Optional[str]=Form(None), params: Params = Depends()):
    '''
    Submit a question to the system. If a question ID is given, retrieve and execute the corresponding query from the QueriesMaster table. Otherwise, generate a new query based on the provided question.
    '''
    add_user_response=AskLLMLogService.askQuestion(request=request,background_tasks=background_tasks,created_by_id=created_by_id,store_id=store_id,role_type=role_type, params=params,question=question,contexts=contexts,question_id=question_id,search_string=search_string,db=db)
    if add_user_response is not None and type(add_user_response)!=int:
        return response_schema.ResponseSchema(status=True, response=msg["search_questions"], data=add_user_response)
    elif add_user_response is not None and type(add_user_response)==int and add_user_response==1:
        return response_schema.ResponseSchema(status=False,response=msg["invalid_question"], data={"message": "Please ask us specific question for which you need response."})
    elif add_user_response is not None and type(add_user_response)==int and add_user_response==3:
        return response_schema.ResponseSchema(status=False,response=msg["no_record_found"], data={"message": "Unable to retrieve any information from your question. Apologies for the inconvenience. We will update our library and get back to you soon."})
    elif add_user_response is not None and type(add_user_response)==int and add_user_response==2:
        return response_schema.ResponseSchema(status=True,response=msg["no_record_found"], data=add_user_response)
    elif add_user_response is not None and type(add_user_response)==int and add_user_response==4:
        return response_schema.ResponseSchema(status=False,response=msg["invalid_question"], data={"message": "Unable to retrieve any information from your question. Apologies for the inconvenience. We will update our library and get back to you soon."})
    else:
        return response_schema.ResponseSchema(status=False,response=msg["no_queries_found"], data={"message":"Unable to retrieve any information from your question. Apologies for the inconvenience. We will update our library and get back to you soon."})


# Follow_up question
@router.post("/follow_up", summary="Follow_up question")
def followUp(params: Params=Depends(),search_string:Optional[str]=Form(None),follow_up_quest: str = Form(),contexts: str = Form(None), role_type:  str = Form(),db: Session = Depends(getDb)):
    '''
    Submit the previous generated query to the context and new follow up question to the question.
    '''
    all_response=vn_helper.followUp(params=params,search_string=search_string,follow_up_quest=follow_up_quest,contexts=contexts,role_type=role_type,db=db)
    if all_response is not None:
        return response_schema.ResponseSchema(status=True, response=msg["search_questions"], data=all_response)
    else:
        return response_schema.ResponseSchema(status=False, response=msg["no_record_found"], data=None)
    
    
# Get search history of asked questions 
@router.get("/search/history", summary="Retrieve the search history of asked questions")
def getQuestions(created_by_id: int,store_id:  Optional[int]=None,params: Params = Depends(),search_string:Optional[str]=None,sort_by: Optional[str] = None,sort_direction: Optional[str] = None,  db: Session = Depends(getDb)):
    all_responses=AskLLMLogService.getQuestions(params=params,created_by_id=created_by_id,store_id=store_id,search_string=search_string, sort_by=sort_by, sort_direction=sort_direction,db=db)
    if all_responses is not None:
        return response_schema.ResponseSchema(response=msg["list_questions"], data=all_responses)
    else:
        return response_schema.ResponseSchema(status=False,response=msg["no_record_found"], data=None)
    

# Validate the query 
@router.post("/validate_query", summary="Node API to Validate a SQL query")
def validateQuery(query: str):
    all_response=Helper.validateQuery(query=query)
    if all_response is not None:
        return response_schema.ResponseSchema(status=True, response=msg["valid_query"], data=all_response)
    elif all_response is not None and type(all_response)==int and all_response==3:
        return response_schema.ResponseSchema(status=False,response=msg["no_record_found"], data={"message": "Unable to retrieve any information from your question. Apologies for the inconvenience. We will update our library and get back to you soon."})
    else:
        return response_schema.ResponseSchema(status=False, response=msg["invalid_query"], data=None)
    