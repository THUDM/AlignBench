from inference.models import api_model
import json
import requests
import zhipuai

zhipuai.api_key = "" # TODO

class chatglm(api_model):
    def __init__(self, workers=10):
        self.model_name = "chatglm_turbo" # TODO
        self.temperature = 0.7
        self.workers = workers

    def get_api_result(self, prompt):
        question = prompt["question"]
        temperature = prompt.get("temperature", self.temperature)

        def single_turn_wrapper(text):
            return [{"role": "user", "content": text}]
        
        response = zhipuai.model_api.invoke(
            model=self.model_name,
            prompt=single_turn_wrapper(question),
            temperature=temperature
        )
        output = response.get("data").get("choices")[0].get("content")
        return output
