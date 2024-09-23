class InvalidStatusCodeError(Exception):
    def __init__(self, message, status_code):
        self.status_code = status_code
        self.message = f"{message} {status_code}"
        super().__init__(self.message)
        
class DecodeJSONError(Exception):
    def __init__(self, message):
        self.message = f"{message}"
        super().__init__(self.message)

class DataValidationError(Exception):
    def __init__(self, message):
        self.message = f"{message}"
        super().__init__(self.message)
 
class InvalidContentJSON(Exception):
    def __init__(self, message):
        self.message = f"{message}"
        super().__init__(self.message)
