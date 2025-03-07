class InvalidCardProccesing(Exception):
    def __init__(self, message, query):
        self.query = query
        self.message = f"{message} {query}"
        super().__init__(self.message)