from inference.models import get_model_api

def test_api_alive(model_name):
    test_prompts = [{
        "question": "你是谁？",
        "temperature": 0}]
    model = get_model_api(model_name, 1)
    if model is None:
        print(">>> invalid model: ", model_name)
        exit(1)
    results = model.generate_text(test_prompts)
    for prompt, res in zip(test_prompts, results):
        print("User:", prompt)
        if res is None:
            print(f">>> api {res} is not alive")
            return False
        print("Assistant:", res)
    return True
