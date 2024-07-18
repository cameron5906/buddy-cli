from models.gpt4o import GPT4OModel

def provide_help(query):
    model = GPT4OModel()
    response = model.generate_help(query)
    print(response)

