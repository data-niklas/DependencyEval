import json
import os
import subprocess
from os import path
from typing import Any, Dict, List

from tqdm import tqdm

from dependency_eval.constants import DOCKER_IMAGE, SALT
from dependency_eval.dataset_utils import (
    get_generated_llm_lsp_code,
    get_generated_vanilla_code,
    get_requirements,
)
from dependency_eval.models import LspGenerationConfig, ModelConfiguration


def get_eval_code(
    item: Dict[str, Any], lsp_generation_config: LspGenerationConfig
) -> str:
    code = (
        get_generated_llm_lsp_code(item)
        if lsp_generation_config.enabled
        else get_generated_vanilla_code(item)
    )
    eval_code = code + "\n" + item["test_code"]
    return eval_code


def get_requirements_file(code_directory: str) -> str:
    return path.join(code_directory, "requirements.txt")


def get_code_file(code_directory: str) -> str:
    return path.join(code_directory, "code.py")


def get_docker_image(python_version):
    return DOCKER_IMAGE.replace("3.7", python_version)


def get_docker_cmd(item: Dict[str, Any], code_file: str, requirements_file: str):
    """Also installs git for pip installs from git repositories"""
    return [
        "docker",
        "run",
        "-it",
        "--rm",
        "--name",
        "dev_dataset_eval_item_" + SALT,
        "-v",
        f"{requirements_file}:/tool/requirements.txt",
        "-v",
        f"{code_file}:/code/llm_lsp_code.py",
        "-w",
        "/code",
        "--cpus",
        "1",
        # "--network", "none", # TODO: use docker build
        get_docker_image(item["python_version"]),
        "sh",
        "-c",
        "apt update >/dev/null 2>/dev/null&& apt install git -y >/dev/null 2>/dev/null && python -m venv /tool/venv && /tool/venv/bin/pip install --upgrade pip 2>/dev/null >/dev/null && /tool/venv/bin/pip install setuptools wheel 2>/dev/null >/dev/null && /tool/venv/bin/pip install -r /tool/requirements.txt 2>error.log >/dev/null && /tool/venv/bin/python llm_lsp_code.py || cat error.log",
    ]


def eval_item(
    configuration: ModelConfiguration,
    item: Dict[str, Any],
    lsp_generation_config: LspGenerationConfig,
    code_directory: str,
):
    eval_code = get_eval_code(item, lsp_generation_config)
    code_file = get_code_file(code_directory)

    requirements = get_requirements(item)
    requirements_file = get_requirements_file(code_directory)

    with open(code_file, "w") as f:
        f.write(eval_code)
    with open(requirements_file, "w") as f:
        f.write(requirements)

    tqdm.write("Running evaluation")
    cmd = get_docker_cmd(item, code_file, requirements_file)
    stdout_text = ""
    try:
        # 2m timeout, as pip install of pytorch takes 80s alone
        output, errors = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        ).communicate(timeout=180)  # TODO: switch to docker build to only timeout test
        stdout_text = output.decode()
        stdout_text = stdout_text.strip()
        if stdout_text.endswith("]") and "[" in stdout_text:
            stdout_text = stdout_text[stdout_text.index("[") :]
        results = json.loads(stdout_text)
        r = ", ".join(map(str, results))
        tqdm.write(f"Test results: {r}")
        item["test_results"] = results
    except Exception as e:
        tqdm.write(f"Error: {e}")
        results = ["error", "error", "error"]
        if lsp_generation_config.enabled:
            item["evaluation_error_llm_lsp"] = stdout_text
        else:
            item["evaluation_error_vanilla"] = stdout_text
    finally:
        subprocess.Popen(
            ["docker", "rm", "dev_dataset_eval_item_" + SALT, "-f"]
        ).communicate()
        os.remove(code_file)
        os.remove(requirements_file)
    return results
