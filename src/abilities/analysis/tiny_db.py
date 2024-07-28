import json
import pandas as pd 
import execnet

from models import ModelTag, TagSelectionMode
from models.base_model_factory import ModelFactory

def handle_analyze_structured_data(df: pd.DataFrame, instructions):
    """
    Queries information from a Pandas dataframe based on the provided instructions.
    
    Args:
        df (pd.DataFrame): The Pandas DataFrame to query
        instructions (str): The instructions for the query
        
    Returns:
        str: The results of the query
    """
    
    # Get the schema of the data
    schema = __generate_schema(df)
    
    # Pick the most intelligent model, or the most balanced one
    model = ModelFactory().get_model(require_vision=False, tags=[ModelTag.MOST_INTELLIGENT, ModelTag.BALANCED], tag_mode=TagSelectionMode.ANY)
    
    # Set up the context
    messages = [
        {
            "role": "system",
            "content": f"""
You will answer questions about a dataset. If asked about its structure, you will refer to the schema provided to you. If asked about the content, you will use the set_python_method tool to query the data.

Querying the data:
You will use TinyDB "User" queries to retrieve specific data or attributes from the dataset. To do this, you will create a "perform_query" method that takes the tinydb "db" object as a parameter.
You will construct a User query based on the instructions provided to you, returning the results.
Your code will be executed using execnet, which means you will need to call channel.send with json.dumps to send the results back to the main process.

Example usage of set_python_method:
Query: Retrieve all entries where the name is "John"
Method:
from tinydb import Query
def perform_query(db):
    User = Query()
    results = db.search(User.name == "John")
    return results
channel.send(json.dumps(perform_query(db)))
---
Query: Retrieve all entries where the age is between 30 and 50
Method:
from tinydb import Query
def perform_query(db):
    User = Query()
    results = db.search(User.age > 30 and User.age < 50)
    return results
channel.send(json.dumps(perform_query(db)))
---
Query: Select all first names where the person is over 40 years old
Method:
from tinydb import Query
def perform_query(db):
    User = Query()
    results = db.search((User.age > 40) & (User.name != None))
    results = [entry["name"].split()[0] for entry in results]
    return results
channel.send(json.dumps(perform_query(db)))

Answering schema questions:
You will use the schema information provided to you in order to answer questions about columns or other structural aspects of the data.

Providing your answer:
In order for the user to receive the information they are looking for, you will need to use the provide_answer tool to provide your answer in a way that is clear and concise.
"""
        },
        {
            "role": "user",
            "content": f"""
The schema of the data is as follows:
{schema}         
"""
        },
        {
            "role": "user",
            "content": instructions
        }
    ]
    
    # Set up the tools
    tools = [
        model.make_tool(
            "set_python_method",
            "Used to provide the Python method that will query the tinyDB instance",
            {"python_code": {"type": "string", "description": "A Python method for querying tinydb"}},
            ["python_code"]
        ),
        model.make_tool(
            "provide_answer",
            "Used to provide your answer to the user",
            {"answer": "string"},
            ["answer"]
        )
    ]
    
    # Attempt a maximum of 3 times to get a successful response
    attempts = 0
    while attempts < 3:
        attempts += 1
        response = model.run_inference(messages=messages, tools=tools, temperature=0.1, require_tool_usage=True)
        
        messages.append(response.choices[0].message)
        
        # Check for a Python query
        set_python_call_id, set_python_args, set_python_call = model.get_tool_call("set_python_method", response)
        if set_python_call_id is not None:
            code = set_python_args["python_code"]

            try:
                # Prepend the provided code with the necessary imports and setup to query TinyDB
                code = f"""
import json
import pandas as pd
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

data = channel.receive()

db = TinyDB(storage=MemoryStorage)
db.insert_multiple(data)

{code}
"""

                # Create an execution gateway for the code
                gw = execnet.makegateway()
                channel = gw.remote_exec(code)
                
                # Execute the query
                channel.send(df.to_dict(orient="records"))
                
                # Receive the results
                exec_result = json.loads(channel.receive())
                
                # Close the gateway
                gw.exit()

                # Build the results into a string format                
                if isinstance(exec_result, list):
                    results = pd.DataFrame(exec_result)
                    results_str = results.to_markdown() if not results.empty else "No results found."
                else:
                    results_str = json.dumps(exec_result, indent=4)
                    
                results_str = f"{results_str}\n\nUse the provide_answer tool to provide your answer."
                
                # Provide the results back to the model
                messages.append(model.make_tool_result(set_python_call, results_str))
                
                attempts-=1
            except Exception as e:
                # Allow the model to correct for errors, and re-affirm the instructions
                messages.append(model.make_tool_result(set_python_call, f"""
The Python code you provided is not functional.
The error message is: {str(e)}
Please make sure you are importing Query from tinydb and are using the correct tinydb syntax, as well as providing a query that matches the data structure and instructions.                                                    
"""))
                continue
        
        # Check for an answer
        provide_answer_id, provide_answer_args, _ = model.get_tool_call("provide_answer", response)
        if provide_answer_id is not None:
            return provide_answer_args["answer"]
            
    return "I failed to find the information due to the complexity of the query. Please try again with a simpler query."

def __generate_schema(data):
    """
    Generate a JSON schema for a given Pandas DataFrame using recursion.

    Args:
        data (pd.DataFrame): The DataFrame to generate a schema for

    Raises:
        ValueError: If the input data is not a DataFrame

    Returns:
        dict: The JSON schema for the DataFrame
    """
    
    if isinstance(data, pd.DataFrame):
        schema = {"type": "object", "properties": {}}
        for column in data.columns:
            if column.startswith("_"):
                continue
            
            col_type = __dtype_to_json_schema(data[column].dtype)
            # Check if the column contains nested structures like lists or dicts
            if col_type == "string" and isinstance(data[column].iloc[0], (list, dict)):
                schema["properties"][column] = __generate_nested_schema(data[column].iloc[0])
            else:
                schema["properties"][column] = {"type": col_type}
        return schema
    else:
        raise ValueError("Input data must be a Pandas DataFrame")


# Function to handle nested structures within DataFrame cells
def __generate_nested_schema(value):
    """
    Generate a nested JSON schema for a given value.

    Args:
        value: The JSON value to generate a schema for

    Returns:
        dict: The nested JSON schema
    """
    
    if isinstance(value, dict):
        schema = {"type": "object", "properties": {}}
        for key, val in value.items():
            if key.startswith("_"):
                continue
            
            schema["properties"][key] = __generate_nested_schema(val)
        return schema
    elif isinstance(value, list):
        return {"type": "array", "items": __generate_nested_schema(value[0]) if value else {}}
    else:
        return {"type": __dtype_to_json_schema(value)}


def __dtype_to_json_schema(dtype):
    """
    Convert Pandas dtype to JSON schema type.

    Args:
        dtype (dtype): The Pandas data type to convert

    Returns:
        str: The corresponding JSON schema type
    """
    
    if pd.api.types.is_integer_dtype(dtype):
        return "integer"
    elif pd.api.types.is_float_dtype(dtype):
        return "number"
    elif pd.api.types.is_bool_dtype(dtype):
        return "boolean"
    elif pd.api.types.is_object_dtype(dtype):
        return "string"  # Default to string for object dtype, could be further refined
    else:
        return "string"  # Fallback to string for any other types
