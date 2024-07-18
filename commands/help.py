from models.gpt4o import GPT4OModel


def provide_help(query):
    model = GPT4OModel()
    model.generate_help(query)

