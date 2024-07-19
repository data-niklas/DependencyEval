import os
from datetime import datetime
from os import path
from shutil import rmtree
from typing import Dict, Any
import json

import click
from tqdm import tqdm

from dependency_eval import VERSION
from dependency_eval.dataset_utils import get_code_directory
from dependency_eval.eval import eval_item
from dependency_eval.generate import run_neural_code_completion
from dependency_eval.loader import (
    load_dataset,
    read_generation_results,
    read_model_configurations,
)
from dependency_eval.loop import run_loop
from dependency_eval.models import LspGenerationConfig, ModelConfiguration
from dependency_eval.venv_cache import get_venv_for_item
from dependency_eval.build import build_dataset, replace_version, update_version


def output_path(configuration: ModelConfiguration, results):
    file_name = configuration.name + ".json"
    return path.join(results, file_name)


PROJECT_BASE_PATH = path.dirname(path.dirname(__file__))
DATASET_PATH = path.join(PROJECT_BASE_PATH, "data")

DATASET_DIST_PATH = path.join(DATASET_PATH, "dist")
EVALUATION_RESULT_PATH = path.join(PROJECT_BASE_PATH, "results", "evaluations")
MODEL_CONFIGURATIONS_PATH = path.join(PROJECT_BASE_PATH, "model_configurations")

DEFAULT_DATASET_VERSION = VERSION
DEFAULT_DATASET_PATH = path.join(
    DATASET_DIST_PATH, f"DependencyEval_{DEFAULT_DATASET_VERSION}.jsonl"
)
DEFAULT_VENV_CACHE_DIRECTORY = path.join(PROJECT_BASE_PATH, "venv_cache")

TODAY = datetime.now().date().strftime("%Y-%m-%d")
DEFAULT_EVALUATION_RESULT_PATH = path.join(EVALUATION_RESULT_PATH, TODAY)


@click.group()
@click.version_option(VERSION)
@click.pass_context
def cli(ctx):
    ctx.obj = None


@cli.command()
@click.option(
    "-t",
    "--update-type",
    type=click.Choice(["major", "minor", "patch"], case_sensitive=False),
)
@click.pass_obj
def build(args, update_type):
    new_version = update_version(update_type)
    replace_version(new_version)
    build_dataset(DATASET_PATH, new_version)


@cli.command()
@click.option("--llm-lsp-directory", required=True)
@click.option("--venv-cache-directory", default=DEFAULT_VENV_CACHE_DIRECTORY)
@click.option("--dataset-file", default=DEFAULT_DATASET_PATH)
@click.option("--results-directory", default=DEFAULT_EVALUATION_RESULT_PATH)
@click.option("--model-configurations-directory", default=MODEL_CONFIGURATIONS_PATH)
@click.pass_obj
def all(
    args,
    llm_lsp_directory: str,
    venv_cache_directory: str,
    dataset_file: str,
    results_directory: str,
    model_configurations_directory: str,
):
    model_configurations = read_model_configurations(model_configurations_directory)
    dataset = load_dataset(dataset_file)

    if not path.exists(results_directory):
        os.makedirs(results_directory)

    def model_configuration_finished_cb(model_configuration: ModelConfiguration):
        out_path = output_path(model_configuration, results_directory)
        result = {
            "model": model_configuration.model,
            "config": model_configuration.config,
            "name": model_configuration.name,
            "items": dataset.items,
        }
        with open(out_path, "w") as f:
            f.write(json.dumps(result))

    lsp_generation_config = LspGenerationConfig()

    def item_cb(model_configuration: ModelConfiguration, item: Dict[str, Any]):
        code_directory = get_code_directory(PROJECT_BASE_PATH, item)
        if path.exists(code_directory):
            rmtree(code_directory)
        os.mkdir(code_directory)

        venv_directory = path.join(code_directory, "venv")
        get_venv_for_item(venv_cache_directory, venv_directory, llm_lsp_directory, item)

        lsp_generation_config.enabled = True
        generated_with, generated_with_log = run_neural_code_completion(
            model_configuration,
            item,
            lsp_generation_config,
            venv_directory,
            code_directory,
        )
        item["generated_code_llm_lsp"] = generated_with
        item["generation_log_llm_lsp"] = generated_with_log

        lsp_generation_config.enabled = False
        generated_without, generated_without_log = run_neural_code_completion(
            model_configuration,
            item,
            lsp_generation_config,
            venv_directory,
            code_directory,
        )
        item["generated_code_vanilla"] = generated_without
        item["generation_log_vanilla"] = generated_without_log

        lsp_generation_config.enabled = True
        eval_results_with = eval_item(
            model_configuration, item, lsp_generation_config, code_directory
        )
        item["evaluated_code_llm_lsp"] = eval_results_with

        lsp_generation_config.enabled = False
        eval_results_without = eval_item(
            model_configuration, item, lsp_generation_config, code_directory
        )
        item["evaluated_code_vanilla"] = eval_results_without
        rmtree(code_directory)

    run_loop(model_configurations, dataset, model_configuration_finished_cb, item_cb)


@cli.command()
@click.option("--dataset-file", default=DEFAULT_DATASET_PATH)
@click.option("--llm-lsp-directory", required=True)
@click.option("--venv-cache-directory", default=DEFAULT_VENV_CACHE_DIRECTORY)
@click.pass_obj
def create_venvs(
    args, dataset_file: str, llm_lsp_directory: str, venv_cache_directory: str
):
    dataset = load_dataset(dataset_file)
    for item in tqdm(dataset.items):
        tqdm.write(item["task_name"])
        get_venv_for_item(venv_cache_directory, None, llm_lsp_directory, item)


if __name__ == "__main__":
    cli()
