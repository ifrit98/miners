import time
import argparse
import bittensor
import openminers
from typing import List, Dict
import os
from llama_cpp import Llama


class LlamaCppMiner(openminers.BasePromptingMiner):
    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
        parser.add_argument("--llamacpp.model_path", type=str, required=True, help="Path to the model file.")
        parser.add_argument("--llamacpp.n_gpu_layers", type=int, default=48, help="Number of GPU layers to use.")

    @classmethod
    def config(cls) -> "bittensor.Config":
        parser = argparse.ArgumentParser(description="LlamaCppMiner Configs")
        cls.add_args(parser)
        return bittensor.config(parser)

    def __init__(self, config: 'bittensor.Config', *args, **kwargs):
        super(LlamaCppMiner, self).__init__(*args, **kwargs)
        self.llm = Llama(model_path=self.config.miner.llama.cpp.model_path, n_gpu_layers=self.config.miner.llama.cpp.n_gpu_layers)

    def forward(self, messages: List[Dict[str, str]]) -> str:
        output = self.llm(
            "Question: {} Answer: ".format(messages[0]['text']),
            max_tokens=48,
            stop=["Q:", "\n"],
            echo=True,
        )
        text = output['choices'][0]['text']
        return text

if __name__ == "__main__":
    config = LlamaCppMiner.config()
    miner = LlamaCppMiner(config=config)
    with miner:
        while True:
            print("running...", time.time())
            time.sleep(1)
