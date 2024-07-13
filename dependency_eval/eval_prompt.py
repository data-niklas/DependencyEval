import logging

logging.disable(logging.INFO)
import traceback

import transformers

transformers.logging.set_verbosity_error()

import asyncio
import json
import sys
from asyncio import CancelledError
from os import path

import nest_asyncio
import torch
from llm_lsp.config import LspGenerationConfig
from llm_lsp.generator import Generator
from transformers import AutoModelForCausalLM, AutoTokenizer

nest_asyncio.apply()


async def main():
    code_file = sys.argv[1]
    model_name = sys.argv[2]
    generation_config = json.loads(sys.argv[3])
    lsp_generation_config = json.loads(sys.argv[4])
    code_dir = path.dirname(code_file)

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map="cuda",
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    config = LspGenerationConfig(**lsp_generation_config)
    generator = Generator(model, tokenizer, generation_config, config=config)

    with open(code_file, "r") as f:
        code = f.read()
    try:
        generated_code = await generator.complete(code, code_dir)
    except Exception:
        generated_code = traceback.format_exc()
    print(generated_code)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except CancelledError:
        traceback.print_exc()
    except Exception:
        traceback.print_exc()
