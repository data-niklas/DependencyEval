import logging

logging.disable(logging.INFO)
import transformers
import traceback
transformers.logging.set_verbosity_error()

import asyncio
import os
from os import path
import json
import sys
from asyncio import CancelledError

from llm_lsp.generator import Generator
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

import nest_asyncio

nest_asyncio.apply()


async def main():
    code_file = sys.argv[1]
    model_name = sys.argv[2]
    generation_config = json.loads(sys.argv[3])
    with_llm_lsp = json.loads(sys.argv[4])
    disabled = not with_llm_lsp
    code_dir = path.dirname(code_file)

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map="cuda",
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token_id = tokenizer.eos_token_id

    generator = Generator(model, tokenizer, generation_config, disabled=disabled)

    with open(code_file, "r") as f:
        code = f.read()
    try:
        generated_code = await generator.complete(code, code_dir)
    except Exception as e:
        generated_code = traceback.format_exc()
    print(generated_code)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except CancelledError as e:
        traceback.print_exc()
    except Exception as e:
        traceback.print_exc()
