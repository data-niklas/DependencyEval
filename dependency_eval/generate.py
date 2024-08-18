import json
import os
import subprocess
import time
from dataclasses import asdict
from os import path
from typing import Any, Dict

from logzero import logger
from tqdm import tqdm

from dependency_eval.constants import EVAL_PROMPT_FILE, LOG_FILE
from dependency_eval.dataset_utils import get_completion_code
from dependency_eval.models import LspGenerationConfig, ModelConfiguration


def get_code_file(code_directory: str) -> str:
    return path.join(code_directory, "code.py")


def run_neural_code_completion(
    model_configuration: ModelConfiguration,
    item: Dict[str, Any],
    lsp_generation_configuration: LspGenerationConfig,
    venv_directory: str,
    code_directory: str,
    llm_lsp_venv_directory: str
):
    """Will consume the lsp generation"""
    lsp_generation_configuration.chat_history_log_file = LOG_FILE
    lsp_generation_configuration_dict = asdict(lsp_generation_configuration)

    completion_code = get_completion_code(item)
    code_file = get_code_file(code_directory)

    with open(code_file, "w") as f:
        f.write(completion_code)
    tqdm.write(
        "Running generation "
        + ("with" if lsp_generation_configuration.enabled else "without")
    )
    os.environ["VIRTUAL_ENV"] = venv_directory
    cmd = [
        f"{llm_lsp_venv_directory}/bin/python",
        EVAL_PROMPT_FILE,
        code_file,
        model_configuration.model,
        json.dumps(model_configuration.config),
        json.dumps(lsp_generation_configuration_dict),
    ]
    start_time = time.time()
    output, error = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()
    end_time = time.time()
    generation_duration = end_time - start_time
    generated = output.decode()
    logger.debug(generated)
    if path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            log_content = f.read()
        os.remove(LOG_FILE)
    else:
        log_content = ""
    os.remove(code_file)
    return generated, log_content, generation_duration


def generate_item(
    model_configuration: ModelConfiguration,
    item: Dict[str, Any],
    lsp_generation_config: LspGenerationConfig,
    code_directory: str,
    venv_directory: str,
):
    lsp_configuration = asdict(lsp_generation_config)
    lsp_configuration["chat_history_log_file"] = LOG_NAME
    code = get_completion_code(item)
    code_path = path.join(code_dir, "code.py")
    with open(code_path, "w") as f:
        f.write(code)
    tqdm.write("Running generation " + ("with" if with_llm_lsp else "without"))
    cmd = [
        f"{venv_path}/bin/python",
        EVAL_PROMPT,
        code_path,
        configuration.model,
        json.dumps(configuration.config),
        json.dumps(lsp_configuration),
    ]
    output, error = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()
    generated = output.decode()
    logger.debug(generated)
    with open(LOG_NAME, "r") as f:
        log_content = f.read()
    os.remove(LOG_NAME)
    return generated, log_content
