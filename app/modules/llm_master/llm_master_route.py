
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request
from sqlalchemy.orm import Session
from config.database import getDb, msg
from typing import List, Optional
from fastapi_pagination import Params
from app.dto import response_schema
from app.modules.llm_master.llm_master_service import LlmMasterService

router = APIRouter(prefix="/api/master", tags=["Query Master"])

# Create master table questions
@router.post("/add/questions")
def create_master_question(request: Request,questions: str = Form(),columns_to_view: str = Form(None),query: str = Form(None), role_type:  str = Form(),
                    active: int = Form(),  db: Session = Depends(getDb)):
    add_user_response=LlmMasterService.create_master_question(request=request,columns_to_view=columns_to_view,questions=questions,query=query, role_type=role_type,active=active,db=db)
    if add_user_response is not None and type(add_user_response)!=int:
        return response_schema.ResponseSchema(status=True, response=msg["questions_created"], data=add_user_response.__dict__)
    elif add_user_response is not None and type(add_user_response)==int and add_user_response==1:
        return response_schema.ResponseSchema(status=False, response=msg["store_duplicate_questions"], data=None)
    elif add_user_response is not None and type(add_user_response)==int and add_user_response==2:
        return response_schema.ResponseSchema(status=False, response=msg["more_than_one_duplicate_platform"], data=None)
    elif add_user_response is not None and type(add_user_response)==int and add_user_response==3:
        return response_schema.ResponseSchema(status=False, response=msg["platform_duplicate_questions"], data=None)
    elif add_user_response is not None and type(add_user_response)==int and add_user_response==4:
        return response_schema.ResponseSchema(status=False, response=msg["more_than_one_duplicate_store"], data=None)
    elif add_user_response is not None and type(add_user_response)==int and add_user_response==5:
        return response_schema.ResponseSchema(status=False,response=msg["save_question"], data=None)
    else:
        return response_schema.ResponseSchema(status=False,response=msg["something_went_wrong"], data=None)


# Update master questions
@router.put("/update/questions/{question_id}")
def updateMasterQuestion(question_id: int, request: Request, questions: str = Form(), query: str = Form(),
                           role_type: str = Form(), active: int = Form(), db: Session = Depends(getDb),columns_to_view: str = Form()):
    updated_response = LlmMasterService.updateMasterQuestion(question_id=question_id, request=request,
                                                                  questions=questions, query=query,
                                                                  role_type=role_type, active=active, db=db,columns_to_view=columns_to_view)
    if updated_response is not None and type(updated_response)!=int:
        return response_schema.ResponseSchema(status=True, response=msg["updtaed_questions"],data=None)
    elif updated_response is not None and type(updated_response)==int and updated_response==1:
        return response_schema.ResponseSchema(status=False,response=msg["save_question"], data=None)
    else:
        return response_schema.ResponseSchema(status=False,response=msg["something_went_wrong"], data=None)
    
    
# List of all master table questions
@router.get("/list", summary="Get all questions")
def listMasterQuestion(params: Params = Depends(),active_status: Optional[int] = None, role_type: Optional[str] = None,query_status:Optional[str]=None,search_string:Optional[str]=None,sort_by: Optional[str] = None,sort_direction: Optional[str] = None,  db: Session = Depends(getDb)):
    all_responses=LlmMasterService.listMasterQuestion(params=params,active_status=active_status, role_type=role_type,query_status=query_status,search_string=search_string, sort_by=sort_by, sort_direction=sort_direction,db=db)
    if all_responses is not None:
        return response_schema.ResponseSchema(status= True,response=msg["list_questions"], data=all_responses)
    else:
        return response_schema.ResponseSchema(status=False,response=msg["no_record_found"], data=None)


# Get master questions by id  
@router.get("/get/question/{question_id}", summary="Get questions by id")
def getMasterQuestion(question_id: int, db: Session = Depends(getDb)):
    all_responses=LlmMasterService.getMasterQuestion(question_id=question_id,db=db)
    if all_responses is not None:
        return response_schema.ResponseSchema(status=True,response=msg["question_found"], data=all_responses.__dict__)
    else:
        return response_schema.ResponseSchema(status=False,response=msg["no_record_found"], data=None)
    

# Delete master questions
@router.post("/delete/questions")
def deleteMasterQuestions(question_ids: str = Form(), db: Session = Depends(getDb)):
    try:
        question_ids_list = [int(id.strip()) for id in question_ids.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid question_ids format. Must be a comma-separated list of integers.")

    delete_response = LlmMasterService.deleteMasterQuestions(question_ids=question_ids_list, db=db)
    if delete_response:
        return response_schema.ResponseSchema(status=True, response=msg["deleted_questions"], data=None)
    else:
        return response_schema.ResponseSchema(status=False, response=msg["no_record_found"], data=None)
    

# Get random questions
@router.get("/random/list/{role_id}", summary="Get Random Questions")
def getRandomQuestions(role_id: int,db: Session = Depends(getDb)):
    # page=1
    # size=5
    all_responses=LlmMasterService.getRandomQuestions(role_id=role_id,db=db)
    if all_responses is not None:
        return response_schema.ResponseSchema(status= True,response=msg["list_questions"], data=all_responses)
    else:
        return response_schema.ResponseSchema(status=False,response=msg["no_record_found"], data=None)
    
    
# Validate the query
@router.post("/validate/queries", summary="Validate Queries")
def validateMasterQuery(query: str = Form()):
    validate_response = LlmMasterService.validateMasterQuery(query=query)
    if validate_response is True:
        return response_schema.ResponseSchema(status=True, response=msg["valid_query"], data=None)
    else:
        return response_schema.ResponseSchema(status=False,response=msg["invalid_query"], data=None)
    

#Duplicate Question
@router.post("/duplicate_question/{question_id}", summary="Duplicate an existing question")
def duplicateQuestion(question_id: int, db: Session = Depends(getDb)):
    duplicated_question = LlmMasterService.duplicateQuestion(question_id=question_id, db=db)
    if duplicated_question is not None:
        return response_schema.ResponseSchema(status=True, response=msg["duplicate_question"], data=duplicated_question.__dict__)
    else:
        return response_schema.ResponseSchema(status=False,response=msg["invalid_id"], data=None)