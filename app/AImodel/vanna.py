import json
import os
import traceback
from typing import Any
from dotenv import load_dotenv
from fastapi import APIRouter, Form, HTTPException
import numpy as np
import pandas as pd
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore
from fastapi import HTTPException
from vanna.google import GoogleGeminiChat

load_dotenv(verbose=True)

router = APIRouter(tags=["Vanna"])

class MyVanna(ChromaDB_VectorStore, GoogleGeminiChat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        GoogleGeminiChat.__init__(self, config={'api_key': "AIzaSyAZQAMbGUrkkJjdm3lkdoS1Gh2oHCzeAd8", 'model': "Gemini 1.5 Flash"})

vn = MyVanna()

# class MyVanna(ChromaDB_VectorStore, Ollama):
#     def __init__(self, config=None):
#         ChromaDB_VectorStore.__init__(self, config=config)
#         Ollama.__init__(self, config=config)

# # vn=None
# # vn = MyVanna(config={'model': 'mistral-nemo'})
# vn = MyVanna(config={'model': 'Mistral_tuned_7b'})

vn.connect_to_mysql(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_DATABASE"),
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    # port=os.getenv("DB_PORT")
    port=3306
)

@router.get("/training_data")
def get_training_data():
    try:
        training_data = vn.get_training_data() 
        
        # Convert training_data to JSON-serializable format if it is a DataFrame
        if isinstance(training_data, pd.DataFrame):
            # Remove the 'content' field
            # training_data = training_data.drop(columns=['content'])
            training_data_dict = training_data.to_dict(orient='records')
            return {"training_data": training_data_dict, "length_of_training_data": len(training_data_dict)}
        
        # If training_data is not a DataFrame, attempt to serialize directly
        return training_data
        
    except Exception as e:
        # Get the traceback as a string
        traceback_str = traceback.format_exc()
        print(traceback_str)

        # Get the line number of the exception
        line_no = traceback.extract_tb(e.__traceback__)[-1][1]
        print(f"Exception occurred on line {line_no}")
        return {"error": str(e), "line_no": line_no, "traceback": traceback_str}
    


@router.delete("/delete/training_data")
def remove_training_data(id : str):
    try:
        delete_data = vn.remove_training_data(id)
        return delete_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/sql_query")
def generate_sql(question: str = Form()):
    try:
        training_data = vn.generate_sql(question)
        # return {"id" :training_data.id,"question": training_data.question, "training_data_type": training_data.training_data_type}
        return training_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        

def replace_nan_with_none(df: pd.DataFrame) -> pd.DataFrame:
    """Replace NaN values with None in a DataFrame."""
    return df.applymap(lambda x: None if pd.isna(x) else x)

def make_serializable(obj: Any) -> Any:
    try:
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.DataFrame):
            # Replace NaN with None before converting
            obj = replace_nan_with_none(obj)
            return obj.to_dict(orient='records')
        elif isinstance(obj, pd.Series):
            return obj.to_dict()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()  # Convert Timestamp to ISO 8601 string
        elif isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(i) for i in obj]
        elif hasattr(obj, '__dict__'):
            return {k: make_serializable(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
        elif isinstance(obj, tuple):
            return tuple(make_serializable(i) for i in obj)
        elif isinstance(obj, set):
            return {make_serializable(i) for i in obj}
        elif obj is None or isinstance(obj, (str, bool, int, float)):
            return obj
        else:
            return str(obj)  # Convert other types to string
    except Exception as e:
        print(f"Error during serialization: {e}")
        raise HTTPException(status_code=500, detail="Serialization error occurred.")

@router.post("/ask")
async def ask_question(question: str = Form(...)):
    try:
        response = vn.ask(question=question)
        # print("Raw Response:============================================================================= ", type(response), response)  # Debug raw response
        # serializable_response = make_serializable(response)
        # print("Serialized Response: ================================================", type(serializable_response), serializable_response)
        # # return ResponseSchema(status=True, response="AI Response", data=serializable_response)
        # return serializable_response
        # Convert training_data to JSON-serializable format if it is a DataFrame
        if isinstance(response, pd.DataFrame):
            # Remove the 'content' field
            # training_data = training_data.drop(columns=['content'])
            training_data_dict = response.to_dict(orient='records')
            return {"training_data": training_data_dict, "length_of_training_data": len(training_data_dict)}
    except Exception as e:
        # Log the detailed traceback
        traceback_str = traceback.format_exc()
        print("Exception occurred:", e)
        print("Traceback:", traceback_str)

        raise HTTPException(status_code=500, detail="An internal error occurred.")