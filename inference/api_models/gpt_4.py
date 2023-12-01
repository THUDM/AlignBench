from inference.models import api_model
from openai import OpenAI
import json

class gpt_4(api_model):
    def __init__(self, workers=10):
        self.workers = workers
        self.model_name = "gpt-4"
        self.temperature = 0.7

    def get_api_result(self, sample):
        question = sample["question"]
        temperature = sample.get("temperature", self.temperature) 

        def single_turn_wrapper(text):
            return [{"role": "user", "content": text}]

        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_name,
            messages=single_turn_wrapper(question),
            temperature=temperature
        )

        output = response.choices[0].message.content
        return output