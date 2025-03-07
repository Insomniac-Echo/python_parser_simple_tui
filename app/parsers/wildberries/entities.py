class DataValidationError(Exception):
    def __init__(self):
        #self.message = f"{message}"
        super().__init__(self)
 
class InvalidContentJSON(Exception):
    def __init__(self):
        #self.message = f"{message}"
        super().__init__(self)
# Необходимость эксепшенов пока под вопросом, возможно они нам не пригодятся