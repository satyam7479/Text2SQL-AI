import random
import traceback
from fastapi import Depends, Form,  Request
from sqlalchemy.orm import Session
from app.models.llm_master_model import QueriesMaster
from config.database import getDb
from dotenv import load_dotenv
from datetime import datetime
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import Optional
import sqlparse
from app.helper.general_helper import Helper

load_dotenv(verbose=True)

class LlmMasterService:

    # Create master table questions
    def create_master_question(request: Request,questions: str = Form(),columns_to_view: str = Form(),query: str = Form(), role_type:  str = Form(),
                        active: int = Form(),  db: Session = Depends(getDb)):
            try:
                if Helper.isQuestion(questions) is False:
                    return 5
                # Define platform and store lists
                store = ['2', '3', '4', '5']
                platform = ['1', '6']
                # Check if the role type is in store or platform
                if role_type in ['2', '3', '4', '5']:  # Store
                    # Check for duplicate questions in store
                    duplicate_store_question = db.query(QueriesMaster).filter(
                        QueriesMaster.questions == questions,
                        QueriesMaster.role_type.in_(store)
                    ).first()
                    if duplicate_store_question:
                        return 1
                    # Check for duplicate questions in platform
                    duplicate_platform_question = db.query(QueriesMaster).filter(
                        QueriesMaster.questions == questions,
                        QueriesMaster.role_type.in_(platform)
                    ).first()
                    if duplicate_platform_question:
                        # Check if more than one duplicate question exists for platform
                        duplicate_count = db.query(QueriesMaster).filter(
                            QueriesMaster.questions == questions,
                            QueriesMaster.role_type.in_(platform)
                        ).count()
                        if duplicate_count > 1:
                            return 2
                        
                elif role_type in ['1', '6']:  # Platform
                    # Check for duplicate questions in platform
                    duplicate_platform_question = db.query(QueriesMaster).filter(
                        QueriesMaster.questions == questions,
                        QueriesMaster.role_type.in_(platform)
                    ).first()
                    if duplicate_platform_question:
                        return 3
                    # Check for duplicate questions in store
                    duplicate_store_question = db.query(QueriesMaster).filter(
                        QueriesMaster.questions == questions,
                        QueriesMaster.role_type.in_(store)
                    ).first()
                    if duplicate_store_question:
                        # Check if more than one duplicate question exists for store
                        duplicate_count = db.query(QueriesMaster).filter(
                            QueriesMaster.questions == questions,
                            QueriesMaster.role_type.in_(store)
                        ).count()
                        if duplicate_count > 1:
                            return 4
                else:
                    return None
                
                add_response = QueriesMaster(
                    questions = Helper.cleanQuestionText(questions),
                    query = query,
                    columns_to_view=columns_to_view,
                    role_type=role_type,
                    added_by="Admin",
                    active = active,
                    created_on=datetime.now(),
                    updated_on = datetime.now()
                )
                db.add(add_response)
                db.commit()
                db.refresh(add_response)
                return add_response

            except Exception as e:
                # Get the traceback as a string
                traceback_str = traceback.format_exc()
                print(traceback_str)

                # Get the line number of the exception
                line_no = traceback.extract_tb(e.__traceback__)[-1][1]
                print(f"Exception occurred on line {line_no}")
                return str(e)


    # Update master questions     
    def updateMasterQuestion(question_id: int, request, questions: str, query: str, role_type: str, active: int, db: Session = Depends(getDb),columns_to_view: str = Form()):
        try:
            if Helper.isQuestion(questions) is False:
                return 1
            existing_question = db.query(QueriesMaster).filter(QueriesMaster.id == question_id).first()
            if existing_question is None:
                return None
            existing_question.questions = Helper.cleanQuestionText(questions)
            existing_question.query = query
            existing_question.role_type = role_type
            existing_question.active = active
            existing_question.updated_on = datetime.now()
            existing_question.columns_to_view = columns_to_view
            db.commit()
            db.refresh(existing_question)
            return True
            
        except Exception as e:
                # Get the traceback as a string
                traceback_str = traceback.format_exc()
                print(traceback_str)

                # Get the line number of the exception
                line_no = traceback.extract_tb(e.__traceback__)[-1][1]
                print(f"Exception occurred on line {line_no}")
                return str(e)
        

    # List of all master table questions 
    def listMasterQuestion(params: Params,active_status: Optional[int] = None,role_type: Optional[str] = None,query_status:Optional[str]=None,search_string:Optional[str]=None,
                    sort_by: Optional[str] = None,sort_direction: Optional[str] = None, db: Session = Depends(getDb)):
        try:
            get_all_questions = db.query(QueriesMaster)
            # Sort_by and sort_direction both logic here
            if sort_direction == "desc":
                get_all_questions = get_all_questions.order_by(QueriesMaster.__dict__[sort_by].desc())
            elif sort_direction == "asc":
                get_all_questions = get_all_questions.order_by(QueriesMaster.__dict__[sort_by].asc())
            else:
                get_all_questions = get_all_questions.order_by(QueriesMaster.id.asc())

            if search_string:
                all_master_questions = get_all_questions.all()
                filtered_questions = [q for q in all_master_questions if Helper.isNearMatch(q.questions, search_string)]
                get_all_questions = db.query(QueriesMaster).filter(QueriesMaster.id.in_([q.id for q in filtered_questions]))

            # Filter based on the presence of a query
            if query_status == "Available":
                get_all_questions = get_all_questions.filter(QueriesMaster.query.isnot(None))
            elif query_status == "Not Available":
                get_all_questions = get_all_questions.filter(QueriesMaster.query.is_(None))

            # Filter based on role type
            if role_type == "Store":
                get_all_questions = get_all_questions.filter(QueriesMaster.role_type.in_(Helper.STORE_ROLE_TYPES))
            elif role_type == "Platform":
                get_all_questions = get_all_questions.filter(QueriesMaster.role_type.in_(Helper.PLATFORM_ROLE_TYPES))

            # Filter based on active status
            if active_status is not None:
                get_all_questions = get_all_questions.filter(QueriesMaster.active == active_status)
            
            # Modify the results to return "Available" or "Not Available" based on the query field
            for question in get_all_questions:
                if question.query is not None:
                    question.query = "Available"
                else:
                    question.query = "Not Available"
            
            get_all_questions=paginate(get_all_questions, params)
            if len(get_all_questions.items) == 0:
                return None
            return get_all_questions
        
        except Exception as e:
            # Get the traceback as a string
            traceback_str = traceback.format_exc()
            print(traceback_str)

            # Get the line number of the exception
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)


    # Get master questions by id
    def getMasterQuestion(question_id: int, db: Session = Depends(getDb)):
        try:
            question = db.query(QueriesMaster).filter(QueriesMaster.id == question_id).first()
            return question
            
        except Exception as e:
            # Get the traceback as a string
            traceback_str = traceback.format_exc()
            print(traceback_str)

            # Get the line number of the exception
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)
        

    # Get random questions
    def getRandomQuestions(role_id: int,db: Session = Depends(getDb)):
        try:
            # Define role types for different conditions
            role_types_1 = [2, 3, 4, 5]
            role_types_2 = [1, 6]

            # Query for questions based on role_id and add active condition
            if role_id in role_types_1:
                questions_with_queries = db.query(QueriesMaster).filter(
                    QueriesMaster.query.isnot(None),
                    QueriesMaster.role_type.in_(role_types_1),
                    QueriesMaster.added_by=="Admin",
                    QueriesMaster.active == True  # Ensure the questions are active
                ).all()
            elif role_id in role_types_2:
                questions_with_queries = db.query(QueriesMaster).filter(
                    QueriesMaster.query.isnot(None),
                    QueriesMaster.role_type.in_(role_types_2),
                    QueriesMaster.added_by=="Admin",
                    QueriesMaster.active == True  # Ensure the questions are active
                ).all()
            else:
                return None
            
            if not questions_with_queries:
                return None
            unique_questions = set()
            random_questions = []
            while len(unique_questions) < 10 and len(unique_questions) < len(questions_with_queries):
                random_question = random.choice(questions_with_queries)
                if random_question not in unique_questions:
                    unique_questions.add(random_question)
                    random_questions.append(random_question)
            return random_questions
            
        except Exception as e:
            # Get the traceback as a string
            traceback_str = traceback.format_exc()
            print(traceback_str)

            # Get the line number of the exception
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)

        

    # Delete master questions
    def deleteMasterQuestions(question_ids: int, db: Session):
        try:
            questions = db.query(QueriesMaster).filter(QueriesMaster.id.in_(question_ids)).all()
            if not questions:
                print("No questions found for the provided IDs.")
                return None
            for question in questions:
                question.deleted_at = datetime.now()
            db.commit()
            return True

        except Exception as e:
            # Get the traceback as a string
            traceback_str = traceback.format_exc()
            print(traceback_str)

            # Get the line number of the exception
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)


    # Validate the query 
    def validateMasterQuery(query: str) -> bool:
        try:
            # Parse the query
            parsed_query = sqlparse.parse(query)
            # Check if the parsed query has at least one statement
            if not parsed_query:
                return False
            # Check if the first token is a valid SQL keyword
            first_token = parsed_query[0].token_first()
            if not first_token or not first_token.is_keyword or first_token.normalized != "SELECT":
                return False
            # Check if the query contains any potentially harmful keywords
            harmful_keywords = {"DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", "CREATE", "ALTER", "GRANT", "REVOKE"}
            for token in parsed_query[0].flatten():
                if token.is_keyword and token.normalized in harmful_keywords:
                    return False
            # If all checks pass, return True
            return True
        
        except Exception as e:
            # Get the traceback as a string
            traceback_str = traceback.format_exc()
            print(traceback_str)

            # Get the line number of the exception
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)


    # Duplicate master question
    def duplicateQuestion(question_id: int, db: Session):
        try:
            original_question = db.query(QueriesMaster).filter(QueriesMaster.id == question_id).first()
            if not original_question:
                return None
            duplicated_question = QueriesMaster(
                questions='',
                query=original_question.query,
                columns_to_view=original_question.columns_to_view,
                role_type=original_question.role_type,
                added_by=original_question.added_by,
                active=original_question.active,
                created_on=datetime.now(),
                updated_on=datetime.now()
            )
            db.add(duplicated_question)
            return duplicated_question

        except Exception as e:
            # Handle exceptions
            traceback_str = traceback.format_exc()
            print(traceback_str)
            
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)
