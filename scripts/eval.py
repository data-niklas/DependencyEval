import json
import os
import subprocess
from argparse import ArgumentParser
from dataclasses import dataclass, asdict
from hashlib import sha256
from os import path
from shutil import rmtree
from typing import Any, Dict, List, Optional
from venv import EnvBuilder

from clonevirtualenv import clone_virtualenv
from logzero import logger
from tqdm import tqdm

EVAL_PROMPT = path.join(path.dirname(__file__), "eval_prompt.py")


@dataclass
class ModelConfiguration:
    model: str
    config: Dict[str, Any]
    name: str


@dataclass
class ModelConfigurationGeneration:
    model: str
    config: Dict[str, Any]
    name: str
    items: List[Dict[str, Any]]


@dataclass
class LspGenerationConfig:
    comments_processor: bool = True
    boundary_processor: bool = True
    lsp_processor: bool = True
    chat_history_log_file: Optional[str] = None
    predict_correct_completion_symbol: bool = True
    force_custom_pad: bool = False
    masked_gen: bool = True
    enabled: bool = (
        True  # quick setting to disable all processors, overrides other settings
    )

GLOBAL_LSP_CONFIGURATION = LspGenerationConfig()

@dataclass
class Dataset:
    name: str
    items: List[Dict[str, Any]]


def read_configurations(directory):
    configurations = []
    for file_name in os.listdir(directory):
        if not file_name.endswith(".json"):
            continue
        file_path = path.join(directory, file_name)
        with open(file_path, "r") as f:
            config = json.loads(f.read())
        configurations.append(
            ModelConfiguration(
                model=config["model"], config=config["config"], name=file_name[:-5]
            )
        )
    return configurations


def read_generation_results(directory):
    configurations = []
    for file_name in os.listdir(directory):
        if not file_name.endswith(".json"):
            continue
        file_path = path.join(directory, file_name)
        with open(file_path, "r") as f:
            config = json.loads(f.read())
        configurations.append(
            ModelConfigurationGeneration(
                model=config["model"],
                config=config["config"],
                name=config["name"],
                items=config["items"],
            )
        )
    return configurations


def load_dataset(dataset_path):
    with open(dataset_path, "r") as f:
        items = [json.loads(i) for i in f.read().splitlines()]
    return Dataset(name=path.basename(dataset_path)[:-6], items=items)


def code_directory(item):
    return path.join(path.dirname(__file__), "eval_code_" + item["task_name"])


def requirements(item):
    requirements = item["package_dependencies"].copy()
    requirements_text = "\n".join(requirements)
    return requirements_text


def create_venv(venv_cache, venv_path, llm_lsp_path, item):
    requirements = item["package_dependencies"].copy()
    requirements_text = "\n".join(requirements)
    requirements_hash = sha256(requirements_text.encode()).hexdigest()
    requirements.append("-e " + llm_lsp_path)
    requirements_text = "\n".join(requirements)
    if not path.exists(venv_cache):
        os.makedirs(venv_cache)
    cached_venv_dir = path.join(venv_cache, requirements_hash)
    if not path.exists(cached_venv_dir):
        tqdm.write("Creating new venv in cache")
        builder = EnvBuilder(
            system_site_packages=False,
            clear=False,
            symlinks=False,  # Important for the Docker container!
            upgrade=False,
            with_pip=True,
            prompt=None,
            upgrade_deps=False,
        )
        builder.create(cached_venv_dir)
        context = builder.ensure_directories(cached_venv_dir)
        requirements_file = "__requirements__.txt"
        with open(requirements_file, "w") as f:
            f.write(requirements_text)
        cmd = [context.env_exec_cmd, "-m", "pip", "install", "packaging", "wheel"]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        cmd = [context.env_exec_cmd, "-m", "pip", "install", "-r", requirements_file]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        os.remove(requirements_file)
    clone_virtualenv(cached_venv_dir, venv_path)


INDENT = "    "


def get_completion_code(item):
    code = "\n".join(item["import_statements"]) + "\n\n"
    if item["context"] != "":
        code += item["context"] + "\n\n"
    code += (
        item["function_signature"]
        + "\n"
        + INDENT
        + item["function_documentation"]
        + "\n"
    )
    return code


def get_generated_vanilla_code(item):
    return get_completion_code(item) + item["generated_code_vanilla"]


def get_generated_llm_lsp_code(item):
    return get_completion_code(item) + item["generated_code_llm_lsp"]


LOG_NAME = "generation_log.log"
def generate_item(
    item, code_dir, venv_path, configuration: ModelConfiguration, with_llm_lsp: bool
):
    lsp_configuration = asdict(GLOBAL_LSP_CONFIGURATION)
    lsp_configuration["enabled"] = with_llm_lsp
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


# Versions larger > 3.7 are not supported by all packages
# Alpine images do not support torch out of the box
DOCKER_IMAGE = "python:3.7-slim-bullseye"


def image(python_version):
    return DOCKER_IMAGE.replace("3.7", python_version)


def eval_item(item, code_dir, configuration: ModelConfiguration, with_llm_lsp: bool):
    code = (
        get_generated_llm_lsp_code(item)
        if with_llm_lsp
        else get_generated_vanilla_code(item)
    )
    eval_code = code + "\n" + item["test_code"]
    code_path = path.join(code_dir, "code.py")
    with open(code_path, "w") as f:
        f.write(eval_code)
    tqdm.write("Running evaluation")
    req = requirements(item)
    requirements_path = path.join(code_dir, "requirements.txt")
    with open(requirements_path, "w") as f:
        f.write(req)
    cmd = [
        "docker",
        "run",
        "-it",
        "--rm",
        "--name",
        "dev_dataset_eval_item",
        "-v",
        f"{requirements_path}:/tool/requirements.txt",
        "-v",
        f"{code_path}:/code/llm_lsp_code.py",
        "-w",
        "/code",
        "--cpus",
        "1",
        # "--network", "none", # TODO: use docker build
        image(item["python_version"]),
        "sh",
        "-c",
        "python -m venv /tool/venv && /tool/venv/bin/pip install -r /tool/requirements.txt 2>error.log >/dev/null && /tool/venv/bin/python llm_lsp_code.py || cat error.log",
    ]
    try:
        # 2m timeout, as pip install of pytorch takes 80s alone
        output, errors = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        ).communicate(timeout=120)  # TODO: switch to docker build to only timeout test
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
        item["test_results"] = results
    finally:
        subprocess.Popen(["docker", "rm", "dev_dataset_eval_item", "-f"]).communicate()
    return results


def output_path(configuration: ModelConfiguration, results):
    file_name = configuration.name + ".json"
    return path.join(results, file_name)


def eval(args):
    configurations = read_generation_results(args.eval)
    venv_cache = args.venv_cache
    results = args.results
    if not os.path.exists(results):
        os.makedirs(results)
    llm_lsp_path = args.llm_lsp_path

    for configuration in tqdm(configurations):
        tqdm.write(f"Running for {configuration.name}")
        for item in tqdm(configuration.items):
            code_dir = code_directory(item)
            if path.exists(code_dir):
                rmtree(code_dir)
            os.mkdir(code_dir)

            if "generated_code_llm_lsp" in item:
                eval_results_with = eval_item(item, code_dir, configuration, True)
                item["evaluated_code_llm_lsp"] = eval_results_with
            if "generated_code_vanilla" in item:
                eval_results_without = eval_item(item, code_dir, configuration, False)
                item["evaluated_code_vanilla"] = eval_results_without
            rmtree(code_dir)

        out_path = output_path(configuration, results)
        result = {
            "model": configuration.model,
            "config": configuration.config,
            "name": configuration.name,
            "items": configuration.items,
        }
        with open(out_path, "w") as f:
            f.write(json.dumps(result))


def all(args):
    configurations = read_configurations(args.model_configurations)
    venv_cache = args.venv_cache
    dataset = load_dataset(args.dataset)
    results = args.results
    if not os.path.exists(results):
        os.makedirs(results)
    llm_lsp_path = args.llm_lsp_path

    for configuration in tqdm(configurations):
        tqdm.write(f"Running for {configuration.name}")
        for item in tqdm(dataset.items):
            code_dir = code_directory(item)
            if path.exists(code_dir):
                rmtree(code_dir)
            os.mkdir(code_dir)

            venv_path = path.join(code_dir, "venv")
            create_venv(venv_cache, venv_path, llm_lsp_path, item)
            generated_with, generated_with_log = generate_item(
                item, code_dir, venv_path, configuration, True
            )
            item["generated_code_llm_lsp"] = generated_with
            item["generation_log_llm_lsp"] = generated_with_log
            generated_without, generated_without_log = generate_item(
                item, code_dir, venv_path, configuration, False
            )
            item["generated_code_vanilla"] = generated_without
            item["generation_log_vanilla"] = generated_without_log
            eval_results_with = eval_item(item, code_dir, configuration, True)
            item["evaluated_code_llm_lsp"] = eval_results_with
            eval_results_without = eval_item(item, code_dir, configuration, False)
            item["evaluated_code_vanilla"] = eval_results_without
            rmtree(code_dir)

        out_path = output_path(configuration, results)
        result = {
            "model": configuration.model,
            "config": configuration.config,
            "name": configuration.name,
            "items": dataset.items,
        }
        with open(out_path, "w") as f:
            f.write(json.dumps(result))


def main(args):
    if args.action == "all":
        all(args)
    elif args.action == "eval":
        eval(args)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-a", "--action", default="all", choices=["all", "generate", "eval"]
    )
    parser.add_argument("-c", "--venv-cache", default="dataset/venv_cache")
    parser.add_argument("-d", "--dataset", default="dataset/data/dist/DependencyEval_0.2.1.jsonl")
    parser.add_argument(
        "-m", "--model-configurations", default="dataset/model_configurations"
    )
    parser.add_argument(
        "-r", "--results", default="dataset/results/evaluations/2024-07-13"
    )
    parser.add_argument("-l", "--llm-lsp-path", default=".")
    parser.add_argument(
        "-e", "--eval", default="dataset/results/evaluations/2024-07-13"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
