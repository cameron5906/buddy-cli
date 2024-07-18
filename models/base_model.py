class BaseModel:

    def generate_command(self, query):
        raise NotImplementedError("Subclasses should implement this method")
