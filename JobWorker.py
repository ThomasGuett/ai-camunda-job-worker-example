import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
import json
from typing import Dict
from llama_cpp import Llama

from pyzeebe import (
    Job,
    ZeebeWorker,
    create_camunda_cloud_channel,
)
from pyzeebe.errors import BusinessError

async def example_logging_task_decorator(job: Job) -> Job:
    # print(job)
    return job

grpc_channel = create_camunda_cloud_channel(
    client_id="<your-client-id>",
    client_secret="<your-client-secret>",
    cluster_id="<your-cluster-id>",
    region="<your-cluster-region shorthand example: bru-2>",
)

_executor = ThreadPoolExecutor(1)

worker = ZeebeWorker(grpc_channel)

worker.before(example_logging_task_decorator)
worker.after(example_logging_task_decorator)

@worker.task(task_type="ask_local_ai")
def example_task(question: str) -> Dict:
    llm = Llama(model_path="./llama.cpp/models/mistral-7b-instruct-v0.1.Q6_K.gguf")
    output = llm("Q: <s>[INST]" + question + "[/INST] A: ", max_tokens=200, echo=False)
    print(output)
    print(output["choices"][0]["text"])

    return {"output": output["choices"][0]["text"]}

if __name__== "__main__":
    print("starting loop")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(worker.work())