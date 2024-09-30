# ask_llm_log_service file to manage AI and it's responses

import string
import traceback
from dotenv import load_dotenv
from fastapi import Depends, Form,  Request
from sqlalchemy.orm import Session
from app.models.llm_master_model import QueriesMaster
from config.database import getDb
from datetime import datetime
from app.models.ask_llm_log_model import AskllmLogsModel
from fastapi_pagination import Params, paginate as f_paginate
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import Optional
from sqlalchemy import func, or_, text, and_
from app.helper.general_helper import Helper
from app.helper.vanna_helper import Helper as v_helper
from sqlalchemy.exc import SQLAlchemyError
from app.AImodel.vanna import vn
import pandas as pd
from fastapi import BackgroundTasks
from cachetools import LRUCache

cache = LRUCache(maxsize=100)  # Adjust the size as per your needs

load_dotenv(verbose=True)

class AskLLMLogService:

    def generate_followup_in_background(question, sql, data, cache_key):
        df = pd.DataFrame(data)
        followed_up = vn.generate_followup_questions(question=question, sql=sql, df=df)
        cache[cache_key] = followed_up
        return followed_up


    # Ask questions
    def askQuestion(params: Params,request: Request, background_tasks: BackgroundTasks, search_string:Optional[str]=None,question: str = Form(),contexts: str = Form(), store_id:  int = Form(),role_type:  str = Form(),
                        question_id: int = Form(), created_by_id: int = Form(),  db: Session = Depends(getDb)):
            try:
                # If contexts are provided, use the cached response
                if contexts is not None:
                    follow_up_result= v_helper.followUp(params=params,search_string=search_string,follow_up_quest=contexts,contexts=question,role_type=role_type,db=db)
                    return follow_up_result
                if question_id:
                    # Fetch the query directly using the question_id
                    get_query_new = db.query(QueriesMaster).filter(QueriesMaster.id == question_id).first()

                    add_response = AskllmLogsModel(
                        question=get_query_new.questions,
                        master_id=question_id,
                        ip_address=request.client.host,
                        created_by_id=created_by_id,
                        store_id = store_id,
                        created_on=datetime.now()
                    )
                    db.add(add_response)
                    db.commit()
                    db.refresh(add_response)

                    if not get_query_new or get_query_new.query is None:
                        return None

                    query_strings = get_query_new.query
                    clean_query = query_strings.strip()

                    # # Add the conditions to the query
                    clean_query = Helper.addConditions(role_type,clean_query,db)

                    # Check if the query contains store_id and if add_response.store_id is None
                    if '{{store_id}}' in get_query_new.query and add_response.store_id is None:
                        return None
                    query_string = clean_query.replace('{store_id}', str(store_id))
                    clean_query = query_string.strip()
                    
                    query = text(clean_query)
                    
                    print('Final Query: ',query)
                    
                    get_data = db.execute(query)
                    data = get_data.fetchall()

                    # json for plot figure
                    df1 = pd.DataFrame(data)
                    # plotly_fig = v_helper.generatePlotlyFigue(question=question,sql=clean_query,df=df1)
                    plotly_fig=None

                    # Extract table name from query
                    table_name = Helper.extractTableName(query_string)
                    data = Helper.renameColumns(data, table_name,db)

                    if not data:
                        return_data = {}
                        return_data['items'] = []
                        return_data['title'] = get_query_new.questions
                        return return_data

                    result = []
                    for row in data:
                        try:
                            result.append(dict(row))
                        except Exception as e:
                            print(f"Error converting row to dictionary: {row}. Error: {e}")

                    # Apply search filter if search_string is provided
                    if search_string:
                        search_string_lower = search_string.lower()
                        filtered_result = []
                        for row in result:
                            if any(search_string_lower in str(value).lower() for value in row.values()):
                                filtered_result.append(row)
                        result = filtered_result

                    # Return the results with the question's metadata
                    data1 = f_paginate(result, params=params)
                    return_data = {}
                    return_data = data1
                    # df = pd.DataFrame(data)
                    # followed_up = vn.generate_followup_questions(question=question,sql=clean_query, df=df )
                    # return_data.__dict__['follow_up_question']=followed_up
                    return_data.__dict__['plotly_fig_json']=plotly_fig if plotly_fig else None
                    return_data.__dict__["column_to_view"] = get_query_new.columns_to_view
                    return_data.__dict__["title"] = get_query_new.questions

                    cache_key = f"{question}_{clean_query}"

                    if cache_key in cache:
                        followed_up = cache[cache_key]
                        return_data.__dict__['follow_up_question'] = followed_up
                    else:
                        follow_up=AskLLMLogService.generate_followup_in_background(question=question, sql=clean_query, data=data, cache_key=cache_key)
                        return_data.__dict__['follow_up_question'] = follow_up

                    return return_data

                # valid_entities = ["Customer", "Store", "Item", "Order"]
                # lower_question = question.lower()
                # lower_valid_entities = [entity.lower() for entity in valid_entities]
                # if not any(entity in lower_question for entity in lower_valid_entities):
                #     return 2
                
                cleaned_question = Helper.cleanQuestionText(question)
                cleaned_question = Helper.removePunctuation(cleaned_question)
                add_clean_quest = Helper.cleanQuestionText(question)

                if Helper.isQuestion(add_clean_quest) is False:
                    return 1
                
                add_response = AskllmLogsModel(
                    question=add_clean_quest,
                    ip_address=request.client.host,
                    created_by_id=created_by_id,
                    store_id = store_id,
                    created_on=datetime.now()
                )
                db.add(add_response)
                db.commit()
                db.refresh(add_response)

                queries_master_questions = func.replace(QueriesMaster.questions, '', '')
                for char in string.punctuation:
                    queries_master_questions = func.replace(queries_master_questions, char, '')

                # Perform the query with the cleaned question
                get_query = db.query(QueriesMaster).filter(queries_master_questions == cleaned_question, QueriesMaster.active==True).first()
                
                # If the question does not exist in QueriesMaster, insert it
                if get_query is None:
                    vanna_query= v_helper.generateSql(cleaned_question)
                    response = Helper.validateAddSemicolon(vanna_query)

                    # Check if the response is a dictionary
                    if isinstance(response, dict) and 'data' in response and 'all_columns' in response['data']:
                        all_columns_value = response['data']['all_columns']
                    else:
                        raise ValueError("Please ask more refined and specific question!")
                    
                    try:
                        # Execute the vanna_query
                        clean_query = vanna_query.strip()  

                        # Add the conditions to the query
                        clean_query = Helper.addConditions(role_type,clean_query,db)

                        # Check if the query contains store_id and if add_response.store_id is None
                        if '{{store_id}}' in clean_query and add_response.store_id is None:
                            return None
                        query_string = clean_query.replace('{store_id}', str(store_id))
                        clean_query = query_string.strip()
                        query = text(clean_query)

                        print('Final Query: ',query)

                        get_data = db.execute(query)

                    except SQLAlchemyError as e:
                        print(f"SQLAlchemyError occurred: {str(e)}")
                        try:
                            new_query = QueriesMaster(
                                questions=question,  
                                query=None,  
                                columns_to_view=None,  
                                role_type=role_type,  
                                added_by='AI',  
                                active=True,  # Assuming the new entry is active
                                created_on=datetime.now(),
                                updated_on=datetime.now()  
                            )
                            db.add(new_query)
                            db.commit()
                            db.refresh(new_query)
                        except Exception as db_exception:
                            print(f"Error while adding new query to QueriesMaster: {str(db_exception)}")
                        return 3
                    else:
                        new_query = QueriesMaster(
                            questions=add_clean_quest,  
                            query=vanna_query,  
                            columns_to_view=all_columns_value,  
                            role_type=role_type,  
                            added_by='AI',  
                            active=True,  # Assuming the new entry is active
                            created_on=datetime.now(),
                            updated_on=datetime.now()
                        )
                        db.add(new_query)
                        db.commit()
                        db.refresh(new_query)
                        
                        # set active flag for query in logs 
                        add_response.active = True

                        db.commit()
                        db.refresh(add_response)

                        data = get_data.fetchall()

                        # json for plot figure
                        df1 = pd.DataFrame(data)
                        # plotly_fig = v_helper.generatePlotlyFigue(question=question,sql=clean_query,df=df1)
                        plotly_fig=None

                    # Extract table name from query
                    table_name = Helper.extractTableName(vanna_query)
                    data = Helper.renameColumns(data, table_name,db)

                    # if no records found
                    if not data:
                        return_data = {}
                        return_data['items'] = []
                        return_data['title'] = question
                        return return_data

                    result = []
                    for row in data:
                        try:
                            result.append(dict(row))
                        except Exception as e:
                            print(f"Error converting row to dictionary: {row}. Error: {e}")
                    
                    # Apply search filter if search_string is provided
                    if search_string:
                        search_string_lower = search_string.lower()
                        filtered_result = []
                        for row in result:
                            if any(search_string_lower in str(value).lower() for value in row.values()):
                                filtered_result.append(row)
                        result = filtered_result

                    db.commit()
                    db.refresh(add_response)

                    data1=f_paginate(result, params=params)
                    
                    # Define the test variable
                    return_data={}
                    return_data=data1
                    # df = pd.DataFrame(data)
                    # followed_up = vn.generate_followup_questions(question=question,sql=clean_query, df=df )
                    # return_data.__dict__['follow_up_question']=followed_up
                    return_data.__dict__['plotly_fig_json']=plotly_fig if plotly_fig else None
                    return_data.__dict__["column_to_view"]=new_query.columns_to_view
                    return_data.__dict__["title"]=question

                    cache_key = f"{question}_{clean_query}"

                    if cache_key in cache:
                        followed_up = cache[cache_key]
                        return_data.__dict__['follow_up_question'] = followed_up
                    else:
                        follow_up=AskLLMLogService.generate_followup_in_background(question=question, sql=clean_query, data=data, cache_key=cache_key)
                        return_data.__dict__['follow_up_question'] = follow_up

                    return return_data

                else:            
                    # Ensure that get_query.query is not None for proceeding with getting query from master database
                    if get_query.query is None:
                        return None
                    
                    query_strings = get_query.query
                    clean_query = query_strings.strip()

                    # # Add the soft delete and active condition to the query
                    clean_query = Helper.addConditions(role_type,clean_query,db)

                    # Check if the query contains store_id and if add_response.store_id is None
                    if '{{store_id}}' in get_query.query and add_response.store_id is None:
                        return None
                    query_string = clean_query.replace('{store_id}', str(store_id))
                    clean_query = query_string.strip()

                    query = text(clean_query) 

                    print('Final Query: ',query)

                    get_data =db.execute(query)
                    data = get_data.fetchall()

                    # json for plot figure
                    df1 = pd.DataFrame(data)
                    # plotly_fig = v_helper.generatePlotlyFigue(question=question,sql=clean_query,df=df1)
                    plotly_fig=None

                    # Extract table name from query
                    table_name = Helper.extractTableName(query_string)
                    data = Helper.renameColumns(data, table_name,db)
                    
                    # Replace query with the query string
                    add_response.master_id = get_query.id
                    
                    # set active flag for query in logs 
                    add_response.active = True

                    db.commit()
                    db.refresh(add_response)

                    if not data:
                        return_data = {}
                        return_data['items'] = []
                        return_data['title'] = get_query.questions
                        return return_data

                    result = []
                    for row in data:
                        try:
                            result.append(dict(row))
                        except Exception as e:
                            print(f"Error converting row to dictionary: {row}. Error: {e}")
                    
                    # Apply search filter if search_string is provided
                    if search_string:
                        search_string_lower = search_string.lower()
                        filtered_result = []
                        for row in result:
                            if any(search_string_lower in str(value).lower() for value in row.values()):
                                filtered_result.append(row)
                        result = filtered_result

                    data1=f_paginate(result, params=params)
                    # Define the test variable
                    return_data={}
                    return_data=data1
                    # df = pd.DataFrame(data)
                    # followed_up = vn.generate_followup_questions(question=question,sql=clean_query, df=df )
                    # return_data.__dict__['follow_up_question']=followed_up
                    return_data.__dict__['plotly_fig_json']=plotly_fig if plotly_fig else None
                    return_data.__dict__["column_to_view"]=get_query.columns_to_view
                    return_data.__dict__["title"]=get_query.questions

                    cache_key = f"{question}_{clean_query}"

                    if cache_key in cache:
                        followed_up = cache[cache_key]
                        return_data.__dict__['follow_up_question'] = followed_up
                    else:
                        follow_up=AskLLMLogService.generate_followup_in_background(question=question, sql=clean_query, data=data, cache_key=cache_key)
                        return_data.__dict__['follow_up_question'] = follow_up

                    return return_data
                
            # except SQLAlchemyError as e:
                # return {"status": "error", "message": f"Database error: {str(e.orig)}"}
            except ValueError as e:
                return 4
            except Exception as e:
                # Get the traceback as a string
                traceback_str = traceback.format_exc()
                print(traceback_str)

                # Get the line number of the exceptionadd_user_response
                line_no = traceback.extract_tb(e.__traceback__)[-1][1]
                print(f"Exception occurred on line {line_no}")
                return str(e)


    # Get search history of asked questions
    def getQuestions(params: Params, created_by_id: int,store_id: Optional[int]=None,search_string:Optional[str]=None,
                    sort_by: Optional[str] = None,sort_direction: Optional[str] = None, db: Session = Depends(getDb)):
        try:
            subquery = db.query(
                AskllmLogsModel.question,
                func.max(AskllmLogsModel.created_on).label('max_created_on')
            ).group_by(
                AskllmLogsModel.question
            ).subquery()

            latest_questions = db.query(AskllmLogsModel).join(
                subquery,
                and_(
                    AskllmLogsModel.question == subquery.c.question,
                    AskllmLogsModel.created_on == subquery.c.max_created_on
                )
            )
            if store_id:
                latest_questions = latest_questions.filter(
                    and_(
                        AskllmLogsModel.store_id == store_id,
                        AskllmLogsModel.created_by_id == created_by_id
                    )
                )
            else:
                latest_questions = latest_questions.filter(
                    AskllmLogsModel.created_by_id == created_by_id
                )

            if search_string:
                latest_questions = latest_questions.filter(
                    or_(
                        AskllmLogsModel.question == search_string,
                        AskllmLogsModel.question.like("%"+search_string+"%"),
                    )
                )

            if sort_by:
                sort_column = AskllmLogsModel.__dict__.get(sort_by)
                if sort_column is not None:
                    if sort_direction == "desc":
                        latest_questions = latest_questions.order_by(sort_column.desc())
                    elif sort_direction == "asc":
                        latest_questions = latest_questions.order_by(sort_column.asc())
                else:
                    latest_questions = latest_questions.order_by(AskllmLogsModel.id.asc())
            else:
                latest_questions = latest_questions.order_by(AskllmLogsModel.id.asc())
            result = paginate(latest_questions, params)
            if len(result.items) == 0:
                return None
            return result
        except Exception as e:
            # Get the traceback as a string
            traceback_str = traceback.format_exc()
            print(traceback_str)

            # Get the line number of the exception
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)




