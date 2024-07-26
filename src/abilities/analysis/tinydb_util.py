import json
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
import pandas as pd 
from functools import reduce

from models import ModelTag, TagSelectionMode
from models.base_model_factory import ModelFactory

# Define the guide for the custom query language used in this module
INSTRUCTION_GUIDE = """
The propriety query language supports the following operators:
and: Wrap multiple instructions that should be combined with "and"
    - left: list of instructions
    - right: list of instructions
or: Wrap multiple instructions that should be combined with "or"
    - left: list of instructions
    - right: list of instructions
not: Wrap multiple instructions that should be negated
    - instructions: list of instructions
=: Equal to
    - field: str
    - value: any
!=: Not equal to
    - field: str
    - value: any
<: Less than
    - field: str
    - value: any
>: Greater than
    - field: str
    - value: any
<=: Less than or equal to
    - field: str
    - value: any
>=: Greater than or equal to
    - field: str
    - value: any
like: Filter for a field with a value that matches a substring
    - field: str
    - value: any
in: Filter for a field with a value in a list of possible values
    - field: str
    - value: list
is_null: Filter for a field with a null value
    - field: str
    
Instructions can be nested to create complex queries. For example:
{ "operator": "and", "left": [ { "operator": "=", "field": "name", "value": "Alice" }, { "operator": ">", "field": "age", "value": 21 } ], "right": [ { "operator": "or", "left": [ { "operator": "=", "field": "city", "value": "New York" }, { "operator": "=", "field": "city", "value": "Los Angeles" } ], "right": [ { "operator": "not", "instructions": [ { "operator": "=", "field": "state", "value": "California" } ] } ] } ]
This query will filter for records where the name is "Alice" and the age is greater than 21, and either the city is "New York" or "Los Angeles" but not in California.

Or a simple query:
{ "operator": "=", "field": "name", "value": "Alice" }
This query will filter for records where the name is "Alice".

How to negate a query:
{ "operator": "not", "instructions": [ { "operator": "=", "field": "name", "value": "Alice" } ] }
This query will filter for records where the name is not "Alice".
"""


def query_pandas_data_frame(df, instructions):
    """
    Generates a TinyDB query from a given a set of instructions.
    
    Args:
        query (list): The query data structure
        
    Returns:
        
    """
    
    # Get the schema of the data
    schema = __generate_schema(df)
    
    # Set up an in-memory database
    data_dict = df.to_dict(orient="records")
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple(data_dict)
    
    # Pick the most intelligent model, or the most balanced one
    model = ModelFactory().get_model(require_vision=False, tags=[ModelTag.MOST_INTELLIGENT, ModelTag.BALANCED], tag_mode=TagSelectionMode.ANY)
    
    # Set up the model parameters
    messages = [
        {
            "role": "system",
            "content": f"""
You are creating a query based on the schema and instructions provided to you by the user. The query will be using a custom instruction-based language to retrieve the requested information from the document database.
You will use the tools provided to you to construct the query:
- You will provide the finalized query using the provide_query tool.

You will generate the query without seeking any feedback from the user.

The custom query language guide is as follows:
{INSTRUCTION_GUIDE}
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
    tools = [
        model.make_tool(
            "provide_query",
            "Provides the finalized SQL query",
            {"query_json": {"type": "string", "description": "The query in JSON format"}},
            ["query_json"]
        ),
    ]
    
    if len(failed_queries) > 0:
        failed_queries_str = "\n".join(failed_queries)
        
        messages.append({
            "role": "assistant",
            "content": f"""
I've tried the following queries so far, but they have failed:
{failed_queries_str}
I will attempt to generate a fixed query based on the instructions provided.
"""
        })
        
    attempts = 0
    
    while attempts < 10:
        attempts += 1
        response = model.run_inference(messages=messages, tools=tools, temperature=0.0)
        
        messages.append(response.choices[0].message)
        
        provide_query_call_id, provide_query_args, provide_query_call = model.get_tool_call("provide_query", response)
        if provide_query_call_id is not None:
            query = provide_query_args["query_json"]
            try:
                instruction = __generate__instruction(json.loads(query))
            except ValueError as value_error:
                error_message = str(value_error)
                failed_queries.append(f"Query: {query}\nError: {error_message}")
                continue
            
            # Execute the query
            results = db.search(instruction)
            results = pd.DataFrame(results)
            results_str = results.to_markdown() if not results.empty else "No results found."
            
            messages.append(model.make_tool_result(provide_query_call, "Success"))
            return results_str
            
    return "I failed to find the information due to the complexity of the query. Please try again with a simpler query."
    
    
def __generate__instruction(instruction):
    User = Query()
    operator = instruction.get("operator")

    if operator in ["=", "!=", "<", ">", "<=", ">=", "like", "in", "is_null"]:
        field = instruction["field"]
        value = instruction.get("value")

        if operator == "=":
            if value == "*":
                return User[field].exists()
            else:
                return User[field] == value
        elif operator == "!=":
            return User[field] != value
        elif operator == "<":
            return User[field] < value
        elif operator == ">":
            return User[field] > value
        elif operator == "<=":
            return User[field] <= value
        elif operator == ">=":
            return User[field] >= value
        elif operator == "like":
            return User[field].matches(value)
        elif operator == "in":
            return User[field].one_of(value)
        elif operator == "is_null":
            return User[field] == None

    elif operator == "not":
        # Handle "not" with an array of instructions
        queries = [__generate__instruction(instr) for instr in instruction["instructions"]]
        # Combine all the queries using "and" (negate all combined queries)
        return ~queries[0] if len(queries) == 1 else ~reduce(lambda x, y: x & y, queries)

    elif operator == "and":
        # Handle "and" with an array of instructions
        queries = [__generate__instruction(instr) for instr in instruction["left"]]
        if len(queries) == 1:
            return queries[0]
        return reduce(lambda x, y: x & y, queries)

    elif operator == "or":
        # Handle "or" with an array of instructions
        queries = [__generate__instruction(instr) for instr in instruction["left"]]
        if len(queries) == 1:
            return queries[0]
        return reduce(lambda x, y: x | y, queries)

    else:
        raise ValueError(f"Unsupported operator: {operator}")


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
