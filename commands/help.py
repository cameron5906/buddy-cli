from models.gpt4o import GPT4OModel


def provide_help(query):
    """
    Provides help for a given task
    
    Args:
        query (str): The task for which help is required
    """
    model = GPT4OModel()
    model.generate_help(query)

