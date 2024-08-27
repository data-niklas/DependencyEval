import asyncio
import json
import os
import time
from datetime import datetime
from os import path
from shutil import rmtree
from typing import Any, Dict
from dataclasses import asdict

import click
from tqdm import tqdm

from dependency_eval import VERSION
from dependency_eval.build import build_dataset, replace_version, update_version
from dependency_eval.constants import COPILOT_MODEL_CONFIGURATION
from dependency_eval.copilot import (
    create_copilot_lsp,
    ensure_copilot_node_server,
    generate_item_with_copilot,
)
from dependency_eval.dataset_utils import get_code_directory
from dependency_eval.eval import eval_item
from dependency_eval.generate import run_neural_code_completion
from dependency_eval.loader import (
    load_dataset,
    load_lsp_generation_config,
    read_generation_results,
    read_model_configurations,
    load_result_file,
)
from dependency_eval.loop import run_loop
from dependency_eval.models import LspGenerationConfig, ModelConfiguration
from dependency_eval.plots import plot_stats
from dependency_eval.stats import show_result_stats, show_dataset_stats, show_all_results_stats, show_dependencies_stats
from dependency_eval.table import export_table, show_table
from dependency_eval.venv_cache import get_venv_for_item, create_venv


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
DEFAULT_LLM_LSP_VENV_DIRECTORY = path.join(PROJECT_BASE_PATH, "llm_lsp_venv")
DEFAULT_COPILOT_NODE_SERVER_CACHE_DIRECTORY = path.join(
    PROJECT_BASE_PATH, "copilot-node-server"
)
DEFAULT_LSP_GENERATION_CONFIG_PATH = path.join(
    PROJECT_BASE_PATH, "lsp_generation_configs"
)

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
@click.option("-r", "--evaluation-results-directory", required=True)
@click.option("-f", "--evaluation-results-filter", default="")
@click.pass_obj
def evaluation_stats(
    args, evaluation_results_directory: str, evaluation_results_filter: str
):
    show_result_stats(evaluation_results_directory, evaluation_results_filter)

@cli.command()
@click.option("-f", "--evaluation-results-filter", default="")
@click.pass_obj
def all_evaluation_stats(
    args, evaluation_results_filter: str
):
    show_all_results_stats(EVALUATION_RESULT_PATH, evaluation_results_filter)


@cli.command()
@click.option("--dataset-file", default=DEFAULT_DATASET_PATH)
@click.pass_obj
def dataset_stats(args, dataset_file: str):
    show_dataset_stats(dataset_file)


@cli.command()
@click.option("-r", "--evaluation-results-directory", required=True)
@click.option("-p", "--plot-file", default="sankey.png")
@click.pass_obj
def plot_evaluation(args, evaluation_results_directory: str, plot_file: str):
    plot_stats(evaluation_results_directory, plot_file)


@cli.command()
@click.option("-r", "--evaluation-results-directory", required=True)
@click.pass_obj
def show_evaluation_table(args, evaluation_results_directory: str):
    show_table(evaluation_results_directory)


@cli.command()
@click.option("-r", "--evaluation-results-directory", required=True)
@click.option("-e", "--excel-file", default="table.xsls")
@click.pass_obj
def export_evaluation_table(args, evaluation_results_directory: str, excel_file: str):
    export_table(evaluation_results_directory, excel_file)


@cli.command()
@click.option("--llm-lsp-directory", required=True)
@click.option("--venv-cache-directory", default=DEFAULT_VENV_CACHE_DIRECTORY)
@click.option("--dataset-file", default=DEFAULT_DATASET_PATH)
@click.option("--results-directory", default=DEFAULT_EVALUATION_RESULT_PATH)
@click.option("--model-configurations-directory", default=MODEL_CONFIGURATIONS_PATH)
@click.option(
    "--lsp-generation-config-file", default=path.join(DEFAULT_LSP_GENERATION_CONFIG_PATH, "default.json")
)
@click.option("--llm-lsp-venv-directory", default=DEFAULT_LLM_LSP_VENV_DIRECTORY)
@click.option("--model-configuration-filter", default="")
@click.pass_obj
def all(
    args,
    llm_lsp_directory: str,
    venv_cache_directory: str,
    dataset_file: str,
    results_directory: str,
    model_configurations_directory: str,
    lsp_generation_config_file: str,
    llm_lsp_venv_directory: str,
    model_configuration_filter: str,
):
    model_configurations = read_model_configurations(
        model_configurations_directory, model_configuration_filter
    )
    dataset = load_dataset(dataset_file)
    lsp_generation_config = load_lsp_generation_config(lsp_generation_config_file)
    if not path.exists(llm_lsp_venv_directory):
        create_venv(llm_lsp_venv_directory, "-e " + path.abspath(llm_lsp_directory))

    if not path.exists(results_directory):
        os.makedirs(results_directory)

    def model_configuration_finished_cb(model_configuration: ModelConfiguration):
        out_path = output_path(model_configuration, results_directory)
        lsp_generation_config_dict = asdict(lsp_generation_config)
        del lsp_generation_config_dict["chat_history_log_file"]
        del lsp_generation_config_dict["enabled"]
        result = {
            "model": model_configuration.model,
            "config": model_configuration.config,
            "name": model_configuration.name,
            "items": dataset.items,
            "lsp_generation_config": lsp_generation_config_dict,
        }
        with open(out_path, "w") as f:
            f.write(json.dumps(result))

    def maybe_skip_model_configuration_cb(model_configuration: ModelConfiguration):
        out_path = output_path(model_configuration, results_directory)
        return path.exists(out_path)

    def item_cb(model_configuration: ModelConfiguration, item: Dict[str, Any]):
        code_directory = get_code_directory(PROJECT_BASE_PATH, item)
        if path.exists(code_directory):
            rmtree(code_directory)
        os.mkdir(code_directory)

        venv_directory = path.join(code_directory, "venv")
        get_venv_for_item(venv_cache_directory, venv_directory, item)

        lsp_generation_config.enabled = True
        generated_with, generated_with_log, generated_with_duration = (
            run_neural_code_completion(
                model_configuration,
                item,
                lsp_generation_config,
                venv_directory,
                code_directory,
                llm_lsp_venv_directory,
            )
        )
        item["generated_code_llm_lsp"] = generated_with
        item["generation_log_llm_lsp"] = generated_with_log
        item["generation_duration_llm_lsp"] = generated_with_duration

        lsp_generation_config.enabled = False
        generated_without, generated_without_log, generated_without_duration = (
            run_neural_code_completion(
                model_configuration,
                item,
                lsp_generation_config,
                venv_directory,
                code_directory,
                llm_lsp_venv_directory,
            )
        )
        item["generated_code_vanilla"] = generated_without
        item["generation_log_vanilla"] = generated_without_log
        item["generation_duration_vanilla"] = generated_without_duration

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

    run_loop(
        model_configurations,
        dataset,
        model_configuration_finished_cb,
        item_cb,
        maybe_skip_model_configuration_cb,
    )


@cli.command()
@click.option("--dataset-file", default=DEFAULT_DATASET_PATH)
@click.option("--venv-cache-directory", default=DEFAULT_VENV_CACHE_DIRECTORY)
@click.pass_obj
def create_venvs(args, dataset_file: str, venv_cache_directory: str):
    dataset = load_dataset(dataset_file)
    for item in tqdm(dataset.items):
        tqdm.write(item["task_name"])
        get_venv_for_item(venv_cache_directory, None, item)


@cli.command()
@click.option("--dataset-file", default=DEFAULT_DATASET_PATH)
@click.option("--results-directory", default=DEFAULT_EVALUATION_RESULT_PATH)
@click.option(
    "--copilot-node-server-directory",
    default=DEFAULT_COPILOT_NODE_SERVER_CACHE_DIRECTORY,
)
@click.pass_obj
def evaluate_copilot(
    args, dataset_file: str, results_directory: str, copilot_node_server_directory: str
):
    asyncio.run(
        evaluate_copilot_inner(
            args, dataset_file, results_directory, copilot_node_server_directory
        )
    )


async def evaluate_copilot_inner(
    _args, dataset_file: str, results_directory: str, copilot_node_server_directory: str
):
    ensure_copilot_node_server(copilot_node_server_directory)
    dataset = load_dataset(dataset_file)
    lsp_generation_config = LspGenerationConfig()
    model_configuration = COPILOT_MODEL_CONFIGURATION
    out_path = output_path(model_configuration, results_directory)
    result_exists = False

    if not path.exists(results_directory):
        os.makedirs(results_directory)

    if path.exists(out_path):
        _, dataset.items, _ = load_result_file(out_path)
        result_exists = True

    for item in tqdm(dataset.items):
        tqdm.write(item["task_name"])
        code_directory = get_code_directory(PROJECT_BASE_PATH, item)
        if path.exists(code_directory):
            rmtree(code_directory)
        os.mkdir(code_directory)
        if not result_exists:
            lsp = await create_copilot_lsp(
                code_directory, copilot_node_server_directory
            )
            (
                generated_without,
                generated_without_duration,
            ) = await generate_item_with_copilot(item, lsp, code_directory)
            item["generated_code_vanilla"] = generated_without
            item["generation_duration_vanilla"] = generated_without_duration

        lsp_generation_config.enabled = False
        eval_results_without = eval_item(
            model_configuration, item, lsp_generation_config, code_directory
        )
        item["evaluated_code_vanilla"] = eval_results_without
        rmtree(code_directory)

    lsp_generation_config_dict = asdict(lsp_generation_config)
    del lsp_generation_config_dict["chat_history_log_file"]
    del lsp_generation_config_dict["enabled"]
    result = {
        "model": model_configuration.model,
        "config": model_configuration.config,
        "name": model_configuration.name,
        "items": dataset.items,
        "lsp_generation_config": lsp_generation_config_dict,
    }
    with open(out_path, "w") as f:
        f.write(json.dumps(result))



@cli.command()
@click.option("--results-directory", default=DEFAULT_EVALUATION_RESULT_PATH)
@click.pass_obj
def eval(args, results_directory: str):
    for f in os.listdir(results_directory):
        out_path = path.join(results_directory, f)
        model_configuration, dataset_items, lsp_generation_config = load_result_file(out_path)
        for item in tqdm(dataset_items):
            tqdm.write(item["task_name"])
            code_directory = get_code_directory(PROJECT_BASE_PATH, item)
            if path.exists(code_directory):
                rmtree(code_directory)
            os.mkdir(code_directory)
            if "generated_code_llm_lsp" in item:
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
        lsp_generation_config_dict = asdict(lsp_generation_config)
        del lsp_generation_config_dict["chat_history_log_file"]
        del lsp_generation_config_dict["enabled"]
        result = {
            "model": model_configuration.model,
            "config": model_configuration.config,
            "name": model_configuration.name,
            "items": dataset_items,
            "lsp_generation_config": lsp_generation_config_dict,
        }
        with open(out_path, "w") as f:
            f.write(json.dumps(result))



@cli.command()
@click.option("--dataset-file", default=DEFAULT_DATASET_PATH)
@click.option("--venv-cache-directory", default=DEFAULT_VENV_CACHE_DIRECTORY)
@click.option("--out-file", default="dependency_stats.json")
@click.pass_obj
def dependency_stats(
    args,
    dataset_file: str,
    venv_cache_directory: str,
    out_file: str
):
    show_dependencies_stats(dataset_file, venv_cache_directory, out_file)

if __name__ == "__main__":
    cli()
