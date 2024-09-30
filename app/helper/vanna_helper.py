import json
from typing import Optional
from dotenv import load_dotenv
import traceback
from dotenv import load_dotenv
from fastapi import Depends, Form
from fastapi import Depends
import pandas as pd
from sqlalchemy.orm import Session
from config.database import getDb
from sqlalchemy import text
from app.helper.general_helper import Helper as gen_helper
from app.AImodel.vanna import vn
from fastapi_pagination import Params, paginate as f_paginate
from sqlalchemy.exc import SQLAlchemyError
from functools import lru_cache

load_dotenv(verbose=True)

class Helper:

    @lru_cache()  # Can adjust the cache size as per your needs
    def cache_response(follow_up_quest: str, contexts: str):
        # Generate SQL query
        sql_query = vn.generate_sql(question=follow_up_quest, contexts=contexts)
        return sql_query
    
    @lru_cache()
    def generateSql(question: str):
        try:
            training_data = vn.generate_sql(question)
            return training_data
        except Exception as e:
            # Get the traceback as a string
            traceback_str = traceback.format_exc()
            print(traceback_str)

            # Get the line number of the exception
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)
        

    def followUp(params: Params, search_string: Optional[str] = None, follow_up_quest: str = Form(),
                contexts: str = Form(), role_type: str = Form(), db: Session = Depends(getDb)):
        try:
            if contexts:
                # Check if the response is already cached, otherwise cache it
                response = Helper.cache_response(follow_up_quest, contexts)
                try:
                    # # Clean and add conditions
                    clean_query = response.strip()
                    clean_query = gen_helper.addConditions(role_type, clean_query, db)

                    # Finalize query and execute
                    final_query = clean_query.strip()
                    query = text(final_query)
                    print('Final Query: ', final_query)

                    # Execute query
                    get_data = db.execute(query)

                except SQLAlchemyError as e:
                    print(f"SQLAlchemyError occurred: {str(e)}")
                    return 3

                data = get_data.fetchall()

                # Extract table name from query
                table_name = gen_helper.extractTableName(final_query)
                data = gen_helper.renameColumns(data, table_name, db)

                if not data:
                    return_data = {'items': [], 'title': follow_up_quest}
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
                    filtered_result = [row for row in result if any(search_string_lower in str(value).lower() for value in row.values())]
                    result = filtered_result

                data1 = f_paginate(data, params=params)
                return_data = data1
                return_data.__dict__["column_to_view"] = table_name
                return_data.__dict__["title"] = follow_up_quest
                return return_data
            else:
                return None
        except Exception as e:
            traceback_str = traceback.format_exc()
            print(traceback_str)

            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)


    def generatePlotlyFigue(question: str, sql: str, df: pd.DataFrame):
        try:
            code = vn.generate_plotly_code(question=question,sql=sql,df=df)
            fig = vn.get_plotly_figure(plotly_code=code, df=df, dark_mode=False)
            fig_json = fig.to_json()
            data = json.loads(fig_json)

            return data
        except Exception as e:
            # Get the traceback as a string
            traceback_str = traceback.format_exc()
            print(traceback_str)

            # Get the line number of the exception
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)