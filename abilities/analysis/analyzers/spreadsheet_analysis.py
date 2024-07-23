import sys
import pandas as pd
from pandas.errors import DatabaseError, ParserError
import sqlite3
from utils.shell_utils import print_fancy
from models.base_model_factory import ModelFactory


def handle_analyze_spreadsheet(file_path, instructions):
    """
    Analyzes a spreadsheet file and returns the requested information.

    Args:
        file_path (str): The path to the spreadsheet file
        instructions (str): Detailed instructions for what information to retrieve

    Returns:
        str: The analysis results
    """
    print_fancy(f"Opening spreadsheet file: {file_path}: {instructions}", italic=True, color="cyan")
    
    # Get a SQLite3 connection to the spreadsheet data
    conn, df = __spreadsheet_to_sqlite3_dataframe(file_path)
    
    if conn is None:
        print_fancy("Unsupported file extension. Only .xlsx and .csv are supported.", bold=True, color="red")
        sys.exit(1)
    
    failed_queries = []
    attempts = 0
    
    print_fancy("Analyzing the data...", italic=True, color="cyan")
    
    while attempts < 5:
        # Generate a SQL query based on the instructions
        sql_query = __generate_sql_query(df, instructions, failed_queries)
        
        # Execute the query
        try:
            results = pd.read_sql_query(sql_query, conn)
            results_str = results.to_markdown(index=False)
        
            return f"Query used:\n{sql_query}\n\nResults:\n{results_str}"
        except (DatabaseError, ParserError) as e:
            failed_queries.append(f"{sql_query}\n\t{e}")
            attempts += 1
    
    return "Could not generate a query to retrieve the requested information. Too many attempts were made."


def __generate_sql_query(df, instructions, failed_queries):
    """
    Generates a SQL query from the instructions provided.

    Args:
        df (pd.DataFrame): The DataFrame containing the data
        instructions (str): Detailed instructions for what information to retrieve
        failed_queries (list): A list of queries and their exception messages that have been tried so far

    Returns:
        str: The SQL query
    """
    
    # Get the schema of the DataFrame
    schema = df.dtypes.to_dict()
    schema_str = ", ".join([f"{col} {dtype.name}" for col, dtype in schema.items()])
    
    model = ModelFactory().get_model(require_vision=False)
    messages = [
        {
            "role": "system",
            "content": """
You are creating a SQL query based on the schema and instructions provided to you by the user.
The query will be a valid SELECT statement that retrieves the requested information from a SQLite3 database using the table 'data'.
You will use the tools provided to you to construct the query:
- You will provide the finalized query using the provide_query tool.
- You will be able to request samples of data by using the get_samples tool.

You will generate the query without seeking any feedback from the user.
"""
        },
        {
            "role": "user",
            "content": f"""
Here is the schema of the data:
{schema_str}
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
            {"query": "string"},
            ["query"]
        ),
        model.make_tool(
            "get_samples",
            "Retrieves a set of distinct values for a given column in order to understand the data better",
            {"column_name": "string"},
            ["column_name"]
        )
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
    
    sql_query = None
    attempts = 0
    
    while sql_query is None and attempts < 10:
        attempts += 1
        response = model.run_inference(messages=messages, tools=tools, temperature=0.0)
        
        messages.append(response.choices[0].message)
        
        provide_query_call_id, provide_query_call_args, provide_query_call = model.get_tool_call("provide_query", response)
        if provide_query_call_id is not None:
            sql_query = provide_query_call_args["query"]
            messages.append(model.make_tool_result(provide_query_call, "Success"))
            break
        
        get_samples_call_id, get_samples_call_args, get_samples_call = model.get_tool_call("get_samples", response)
        if get_samples_call_id is not None:
            print_fancy(f"Reading some samples from {get_samples_call_args['column_name']}...", italic=True, color="cyan")
            column_name = get_samples_call_args["column_name"]
            
            try:
                samples = df[column_name].dropna().unique()
                samples_str = ", ".join([str(sample) for sample in samples])
                messages.append(model.make_tool_result(get_samples_call, samples_str))
            except KeyError:
                messages.append(model.make_tool_result(get_samples_call, "Column not found"))
            
    return sql_query


def __spreadsheet_to_sqlite3_dataframe(file_path):
    """
    Loads spreadsheet data into a dataframe and sqlite3 memory database.

    Args:
        file_path (str): The path to the spreadsheet file
        
    Returns:
        sqlite3.Connection | None: The sqlite3 connection object or None if the file extension is not supported
        pd.DataFrame: The DataFrame containing the data
    """

    # Get file extension
    file_extension = file_path.split(".")[-1].lower()
    
    if file_extension == "xlsx":
        df = pd.read_excel(file_path)
    elif file_extension == "csv":
        df = pd.read_csv(file_path, delimiter=',', quotechar='"', skipinitialspace=True)
        # Clean up quoted headers and values
        df.columns = df.columns.str.strip().str.replace('"', '')
        df = df.applymap(lambda x: x.strip().replace('"', '') if isinstance(x, str) else x)
    else:
        return None, None
        
    conn = sqlite3.connect(":memory:")
    df.to_sql("data", conn, index=False, if_exists='replace')
    
    return conn, df
