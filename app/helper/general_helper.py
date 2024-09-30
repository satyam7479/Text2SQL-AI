import os
import string
from fastapi import HTTPException
import requests
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from dotenv import load_dotenv
from typing import List
import nltk
import re
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from app.modules.alias_management.alias_management_serevice import ListAliasesService
from column_mapping import EXCLUDED_TABLES

load_dotenv(verbose=True)
dbname=os.getenv("DB_DATABASE")

NODE_API_URL = "https://apilocal.lokaly.in/admin/validate_query"

# Get the root path of the project directory
project_root_path = os.path.abspath(os.path.dirname(__file__))

# Set the nltk_data path to the root of the project
nltk_data_path = os.path.join(project_root_path, 'nltk_data')

os.makedirs(nltk_data_path, exist_ok=True)

# Set the NLTK_DATA environment variable
os.environ['NLTK_DATA'] = nltk_data_path

# Insert the custom path as the first path in nltk.data.path
nltk.data.path.insert(0, nltk_data_path)

# # Download required NLTK packages
# nltk.download('punkt', download_dir=nltk_data_path)
# nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_path)
# nltk.download('stopwords', download_dir=nltk_data_path)
# nltk.download('punkt_tab',download_dir=nltk_data_path)
# nltk.download('averaged_perceptron_tagger_eng',download_dir=nltk_data_path)

class Helper:

    # Define the role type lists
    STORE_ROLE_TYPES = [2, 3, 4, 5]
    PLATFORM_ROLE_TYPES = [1, 6]

    # Initialize sets
    STORE_ID_TABLES = set()
    SELLER_ID_TABLES = set()

    def validateQuery(query: str):
        try:
            # Hardcoded values for database configuration and other parameters
            is_numeric = 1
            db_type = os.getenv("DB_CONNECTION")
            host = os.getenv("DB_HOST")
            port = os.getenv("DB_PORT")
            database = os.getenv("DB_DATABASE")
            username = os.getenv("DB_USERNAME")
            password = os.getenv("DB_PASSWORD")

            # Prepare the JSON payload with hardcoded parameters
            payload = {
                "query": query,
                "is_numeric": is_numeric,
                "dbConfig": {
                    "dbType": db_type,
                    "host": host,
                    "port": port,
                    "database": database,
                    "username": username,
                    "password": password
                }
            }

            # Make the POST request with the payload
            response = requests.post(NODE_API_URL, json=payload)

            # Check if the response status is not 200
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to validate query")

            # Get the response JSON
            validation_result = response.json()

            # Return the validation result
            return validation_result

        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"HTTP error occurred: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
        

    def removePunctuation(text):
        return text.translate(str.maketrans('', '', string.punctuation))


    def cleanQuestionText(text: str) -> str:
        text = re.sub(r'\s+([{}])'.format(re.escape(string.punctuation)), r'\1', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


    def isQuestion(text):
        text = text.strip()
        # if text.endswith('?'):
        #     return True
        # always add words in lower case
        question_words = {'who', 'what', 'where', 'when', 'why', 'how', 'which', 'whom', 'whose','list','give', 'retrieve','fetch','get','find','count'}
        tokens = word_tokenize(text.lower())
        if tokens[0] in question_words:
            return True
        pos_tags = pos_tag(tokens)
        aux_verbs = {'list','give','is', 'are', 'was', 'were', 'do', 'does', 'did', 'have', 'has', 'had', 'can', 'could', 'will', 'would', 'shall', 'should', 'may', 'might', 'must'}
        if pos_tags[0][0] in aux_verbs:
            return True
        return False
    

    # Utility function to split a sentence into words
    def splitIntoWords(sentence: str) -> List[str]:
        return sentence.lower().replace(',', '').replace('.', '').replace('?', '').split()


    # Function to compare the words in search string with the master question
    def isNearMatch(master_question: str, search_string: str) -> bool:
        master_words = set(Helper.splitIntoWords(master_question))
        search_words = set(Helper.splitIntoWords(search_string))
        return search_words.issubset(master_words)


    def visibilityDropColumns(table_name: str, db: Session):
        inspector = inspect(db.bind)
        columns_to_drop = set()
        alias = ListAliasesService.listAliases(db)
        VISIBILITY = alias['VISIBILITY']
        # Check if the table is in the VISIBILITY dictionary
        if table_name in VISIBILITY:
            visibility_columns = set(VISIBILITY[table_name])
            columns_to_drop.update(visibility_columns)

        # Get primary key columns and add to columns_to_drop
        primary_keys = inspector.get_pk_constraint(table_name)['constrained_columns']
        columns_to_drop.update(primary_keys)

        # Get foreign key columns and add to columns_to_drop
        foreign_keys = inspector.get_foreign_keys(table_name)
        for fk in foreign_keys:
            constrained_columns = fk['constrained_columns']
            columns_to_drop.update(constrained_columns)

        return columns_to_drop
    
    
    # Rename column and set priority and also set the visibility
    def renameColumns(result, table_name, db: Session):
        columns_to_drop = Helper.visibilityDropColumns(table_name, db)
        alias = ListAliasesService.listAliases(db)
        COLUMN_MAPPINGS = alias['COLUMN_MAPPINGS']
        COLUMN_PRIORITIES = alias['COLUMN_PRIORITIES']
        if table_name not in COLUMN_MAPPINGS:
            return result
        mapping = COLUMN_MAPPINGS[table_name]
        priority = COLUMN_PRIORITIES.get(table_name, [])
        renamed_result = []

        for row in result:
            # Convert the row to a dictionary if it's not already one
            row_dict = dict(row)
            new_row = {}
            
            # Apply column mapping and skip columns to be dropped
            for key, value in row_dict.items():
                if key in columns_to_drop:
                    continue  # Skip columns that need to be dropped                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
                if key in mapping:
                    new_row[mapping[key]] = value
                else:
                    new_row[key] = value

            # Sort new_row according to the priority list
            sorted_row = {col: new_row[col] for col in priority if col in new_row}
            
            # Add any remaining columns that weren't in the priority list
            for key in new_row:
                if key not in sorted_row:
                    sorted_row[key] = new_row[key]
            renamed_result.append(sorted_row)
        return renamed_result

    
    def extractTableName(query):
        """
        Extracts table names and aliases from a SQL query.
        Returns a list of tuples containing (table_name, alias) or just (table_name, None) if no alias.
        """
        # Updated regex to handle optional alias and cases with or without AS keyword
        table_regex = re.compile(r'(?:FROM|JOIN)\s+`?(\w+)`?(?:\s+(?:AS\s+)?`?(\w+)`?)?', re.IGNORECASE)
        matches = table_regex.findall(query)
        for match in matches:
            table_names = match[0]
            return table_names


    def fetchTablesColumns(db: Session):
        # Query for tables with store_id
        result = db.execute(f"""
            SELECT DISTINCT table_name
            FROM information_schema.columns
            WHERE column_name = 'store_id'
            AND table_schema = '{dbname}';
        """)
        store_id_tables = result.fetchall()
        Helper.STORE_ID_TABLES.update([table[0] for table in store_id_tables])

        # Query for tables with seller_id
        result = db.execute(f"""
            SELECT DISTINCT table_name
            FROM information_schema.columns
            WHERE column_name = 'seller_id'
            AND table_schema = '{dbname}';
        """)
        seller_id_tables = result.fetchall()
        Helper.SELLER_ID_TABLES.update([table[0] for table in seller_id_tables])


    def addConditions(role_type, query, db: Session):
        print("original_query:================", query)
        # Regular expressions for detecting clauses
        where_pattern = re.compile(r'\bWHERE\b', re.IGNORECASE)
        group_by_pattern = re.compile(r'\bGROUP\s+BY\b', re.IGNORECASE)
        order_by_pattern = re.compile(r'\bORDER\s+BY\b', re.IGNORECASE)

        # Detect CTEs and their names
        cte_names = re.findall(r'\bWITH\s+(\w+)\s+AS\s+\(', query, re.IGNORECASE)
        
        # subquery_table_name = re.findall(r'\(\s*select.*?\s+from\s+(\w+)', query, re.IGNORECASE)
        subquery_table_name = re.findall(r'\(\s*select[\s\S]*?\s+from\s+(\w+)', query, re.IGNORECASE)

        # from_join_clause = re.compile(r'(?:FROM|JOIN)\s+(\w+)(?:\s+AS\s+(\w+))?', re.IGNORECASE)
        from_join_clause = re.compile(r'(?:FROM|JOIN)\s+(\w+)(?:\s+(?:AS\s+)?(\w+))?', re.IGNORECASE)

        # List of common SQL keywords to filter out invalid aliases
        sql_keywords = {"WHERE", "GROUP", "ORDER", "BY", "SELECT", "JOIN", "FROM", "AS", "ON", "LIMIT", "AND", "OR", "INNER", "OUTER", "LEFT", "RIGHT"}

        # Extract table aliases (or table names if no alias is provided)
        aliases = []
        table_alias_map = {}  # Map to store table name and alias mapping
        matches = from_join_clause.findall(query)
        for match in matches:
            table_name = match[0]  # Always present
            potential_alias = match[1]  # May be empty

            # If potential_alias is None, empty, or a SQL keyword, use the table name as the alias
            if not potential_alias or potential_alias.upper() in sql_keywords:
                alias = table_name
            else:
                alias = potential_alias

            aliases.append(alias)
            table_alias_map[alias] = table_name
        
        # Remove CTE(Common Table Expression) names from the aliases list if any CTEs are present
        if cte_names:
            aliases = [alias for alias in aliases if alias not in cte_names]

        if subquery_table_name:
            aliases = [alias for alias in aliases if alias not in subquery_table_name]

        # Exclude aliases corresponding to excluded tables
        aliases = [alias for alias in aliases if table_alias_map.get(alias) not in EXCLUDED_TABLES]

        # Dynamically determine condition based on presence of store_id or seller_id
        conditions = []
        found_id = False  # Flag to check if we found store_id or seller_id
        Helper.fetchTablesColumns(db)
        for alias in aliases:
            table_name = table_alias_map.get(alias)
            if table_name in Helper.STORE_ID_TABLES and int(role_type) in Helper.STORE_ROLE_TYPES:
                conditions.append(f'{alias}.store_id = {{store_id}}')
                found_id = True
            elif table_name in Helper.SELLER_ID_TABLES and int(role_type) in Helper.STORE_ROLE_TYPES:
                conditions.append(f'{alias}.seller_id = {{store_id}}')
                found_id = True
            
            conditions.append(f'{alias}.is_deleted=0 AND {alias}.is_active=1')

        # If no table has store_id or seller_id, use the default condition
        if not found_id:
            conditions = [f'{alias}.is_deleted=0 AND {alias}.is_active=1' for alias in aliases]
        condition = ' AND '.join(conditions)

        where_matches = list(where_pattern.finditer(query))
        
        # If there's more than one WHERE, find the right one to modify
        if where_matches:
            for match in where_matches:
                start_pos = match.start()
                
                # Check if this WHERE is inside a subquery
                preceding_query_part = query[:start_pos]
                
                # Count the number of opening and closing parentheses
                open_parens = preceding_query_part.count('(')
                close_parens = preceding_query_part.count(')')
                
                # If it's the same number of open and close, it's an outer WHERE
                if open_parens == close_parens:
                    # Modify the outermost WHERE clause only
                    query = query[:start_pos] + f'WHERE {condition} AND ' + query[start_pos + len('WHERE '):]
                    break

        # Determine if `GROUP BY` or `ORDER BY` clauses exist
        group_by_exists = group_by_pattern.search(query)
        order_by_exists = order_by_pattern.search(query)

        if not where_matches:
            # Insert conditions before `GROUP BY` or `ORDER BY` if they exist
            if group_by_exists:
                query = re.sub(r'\bGROUP\s+BY\b', f'WHERE {condition} \g<0>', query, 1, re.IGNORECASE)
            elif order_by_exists:
                query = re.sub(r'\bORDER\s+BY\b', f'WHERE {condition} \g<0>', query, 1, re.IGNORECASE)
            else:
                # If neither `GROUP BY` nor `ORDER BY` exist, append `WHERE` clause at the end
                query = f'{query} WHERE {condition}'


        # Removing unnecessary `AND` if it's the first condition
        query = re.sub(r'\bWHERE\s+AND\b', 'WHERE', query, re.IGNORECASE)

        # Move any semicolon to the end of the query
        query = query.replace(';', '') 
        query = query.strip() 

        # Add a semicolon at the end if not present
        if not query.endswith(';'):
            query += ';'
        print("modified query:===================",query)

        return query


    def validateAddSemicolon(query):
        if query.strip().endswith(';'):
            result=Helper.validateQuery(query)
            return result 
        else:
            semicolon_query=query.strip() + ';'
            result=Helper.validateQuery(semicolon_query)
            return query.strip() + ';' 