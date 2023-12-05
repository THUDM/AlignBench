import importlib
from tqdm import tqdm
from typing import List
import time
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import logging
logging.basicConfig(level=logging.INFO)

class api_model:
    def __init__(self, workers=20):
        self.workers = workers

    def call_api_in_parallel(self, samples, workers: int, timeout: int = 180) -> List[str]:

        def get_result_with_retry(sample, retries=3, timeout=timeout):

            for i in range(retries):
                try:
                    result = self.get_api_result(sample)
                    return result
                except Exception as e:
                    logging.error(f"call api error encountered in try {i} / {retries}. Error detail: {e}")
                    time.sleep(0)
            return None

        def worker_thread(para):
            sample, index, results = para
            results[index] = get_result_with_retry(sample)

        results = [None] * len(samples)
        paras = [(sample, index, results) for index, sample in enumerate(samples)]
        with ThreadPoolExecutor(workers) as executor:
            for _ in tqdm(
                executor.map(worker_thread, paras), total=len(paras)
            ):
                pass
    
        return results

    def generate_text(self, dataset):
        result = self.call_api_in_parallel(dataset, self.workers)
        return result

    def get_api_result(self, sample):
        pass

def get_model_api(model_name, workers):
    try:
        module_path = f"inference.api_models.{model_name}"
        module = importlib.import_module(module_path)
        model_class = getattr(module, model_name)
        return model_class(workers)
    except Exception as e:
        logging.error(f"error when import module: {module_path} ", e)
        exit(1)
    