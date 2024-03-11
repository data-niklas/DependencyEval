import logging
logging.disable(logging.INFO)
import transformers
transformers.logging.set_verbosity_error()

import asyncio
import os
from os import path
import json
import sys


from llm_lsp.__main__ import create_lsp, initialize_generation, create_generator
from llm_lsp.lsp_processor import LspLogitsProcessor
from llm_lsp.lsp_client import LspClient
from llm_lsp.constants import *
from llm_lsp.generator import LspGenerator
from llm_lsp.interrupts import InterruptStoppingCriteria, Interrupt, handle_deprecation_interrupt, handle_signature_interrupt

import nest_asyncio
nest_asyncio.apply()

async def main():
    code_file = sys.argv[1]
    model = sys.argv[2]
    config = json.loads(sys.argv[3])
    code_dir = path.dirname(code_file)
    generator = await create_generator("COMPLETE", code_dir, model, config)
    with open(code_file, "r") as f:
        code = f.read()
    try:
        generated_code = generator(code, code_file)
    except Exception as e:
        generated_code = "Error: " + str(e)
    print(generated_code)

if __name__ == "__main__":
    asyncio.run(main())