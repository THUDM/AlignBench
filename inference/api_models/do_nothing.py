from inference.models import api_model

class do_nothing(api_model):
    def __init__(self, workers = 10):
        self.temperature = 0.95
        self.max_tokens = 1024
        self.workers = workers

    def get_api_result(self, sample):
        question = sample["question"]
        temperature = sample.get("temperature", self.temperature)
        
        return str(temperature)
