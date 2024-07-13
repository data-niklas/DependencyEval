import asyncio
import json
import os
import subprocess
from argparse import ArgumentParser
from dataclasses import dataclass
from hashlib import sha256
from os import path
from shutil import rmtree
from typing import Any, Dict, List
from venv import EnvBuilder

from clonevirtualenv import clone_virtualenv
from logzero import logger
from lsprotocol.types import *
from pygls.lsp.client import BaseLanguageClient
from tqdm import tqdm

EVAL_PROMPT = path.join(path.dirname(__file__), "eval_prompt.py")


@dataclass
class Dataset:
    name: str
    items: List[Dict[str, Any]]


async def create_copilot_lsp(code_dir):
    copilot_node_server_dir = "copilot-node-server"
    lsp: BaseLanguageClient = BaseLanguageClient("copilot", "1.0.0")
    await lsp.start_io(
        "node",
        path.join(copilot_node_server_dir, "copilot", "dist", "agent.js"),
        "--stdio",
    )
    logger.debug("Started LSP")

    @lsp.feature("workspace/configuration")
    def configuration(ls, params):
        print("It wants configuration!!!")
        logger.debug(params)

    @lsp.feature("window/logMessage")
    def configuration(ls, params):
        print("Log")
        logger.debug(params)

    @lsp.feature("textDocument/publishDiagnostics")
    def diagnostics(ls, params):
        # pass
        diagnostics = [
            d
            for d in params.diagnostics
            if d.tags and DiagnosticTag.Deprecated in d.tags
        ]

    initialize_result = await lsp.initialize_async(
        InitializeParams(
            root_path=code_dir,
            capabilities=ClientCapabilities(
                workspace=WorkspaceClientCapabilities(
                    configuration=True,
                    did_change_configuration=DidChangeConfigurationClientCapabilities(
                        dynamic_registration=True
                    ),
                    workspace_folders=True,
                ),
                text_document=TextDocumentClientCapabilities(
                    completion=CompletionClientCapabilities(
                        completion_item=CompletionClientCapabilitiesCompletionItemType(
                            snippet_support=True,
                            deprecated_support=True,
                            documentation_format=["markdown", "plaintext"],
                            preselect_support=True,
                            label_details_support=True,
                            resolve_support=CompletionClientCapabilitiesCompletionItemTypeResolveSupportType(
                                properties=[
                                    "deprecated",
                                    "documentation",
                                    "detail",
                                    "additionalTextEdits",
                                ]
                            ),
                            tag_support=CompletionClientCapabilitiesCompletionItemTypeTagSupportType(
                                value_set=[CompletionItemTag.Deprecated]
                            ),
                            insert_replace_support=True,
                        )
                    ),
                    publish_diagnostics=PublishDiagnosticsClientCapabilities(
                        tag_support=PublishDiagnosticsClientCapabilitiesTagSupportType(
                            value_set=[DiagnosticTag.Deprecated]
                        )
                    ),
                ),
            ),
        )
    )

    lsp.initialized(InitializedParams())

    lsp.workspace_did_change_configuration(
        DidChangeConfigurationParams(
            settings={
                "http": {"proxy": None, "proxyStrictSSL": None},
                "github-enterprise": {
                    "uri": "https://github.com",
                },
            }
        )
    )
    return lsp


def load_dataset(dataset_path):
    with open(dataset_path, "r") as f:
        items = [json.loads(i) for i in f.read().splitlines()]
    return Dataset(name=path.basename(dataset_path)[:-6], items=items)


def code_directory(item):
    return path.join(path.dirname(__file__), "eval_code_" + item["task_name"])


def create_venv(venv_cache, venv_path, item):
    requirements = item["package_dependencies"].copy()
    requirements_text = "\n".join(requirements)
    requirements_hash = sha256(requirements_text.encode()).hexdigest()
    requirements_text = "\n".join(requirements)
    if not path.exists(venv_cache):
        os.makedirs(venv_cache)
    cached_venv_dir = path.join(venv_cache, requirements_hash)
    if not path.exists(cached_venv_dir):
        tqdm.write("Creating new venv in cache")
        builder = EnvBuilder(
            system_site_packages=False,
            clear=False,
            symlinks=True,
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
        cmd = [context.env_exec_cmd, "-m", "pip", "install", "-r", requirements_file]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        os.remove(requirements_file)
    clone_virtualenv(cached_venv_dir, venv_path)


def get_completion_code(item):
    code = "\n".join(item["import_statements"]) + "\n\n"
    if item["context"] != "":
        code += item["context"] + "\n\n"
    code += item["function_signature"] + "\n  " + item["function_documentation"] + "\n"
    return code


def get_generated_vanilla_code(item):
    return get_completion_code(item) + item["generated_code_vanilla"]


def char_line_of_code(code):
    if code == "":
        return 0, 0
    lines = code.splitlines()
    last_line_index = len(lines) - 1
    last_line = lines[last_line_index]
    last_char_index = len(last_line)
    return max(last_char_index, 0), max(last_line_index, 0)


async def generate_item(item, lsp, code_dir):
    code = get_completion_code(item)
    code_path = path.join(code_dir, "code.py")
    with open(code_path, "w") as f:
        f.write(code)
    uri = "file://" + path.abspath(code_path)
    text_document_item = TextDocumentItem(
        uri=uri,
        language_id="python",
        version=1,
        text=code,
    )
    lsp.text_document_did_open(
        DidOpenTextDocumentParams(text_document=text_document_item)
    )
    char, line = char_line_of_code(code)
    doc = {
        "uri": uri,
        "version": 1,
        "insertSpaces": True,
        "tabSize": 4,
        "indentSize": 4,
        "position": {"line": line, "character": char},
    }
    completions = await lsp.protocol.send_request_async(
        "getCompletions",
        {"doc": doc, "textDocument": {"uri": doc["uri"], "version": doc["version"]}},
    )
    generated = completions.completions[0].text
    return generated


DOCKER_IMAGE = "python:3.8-alpine"


def eval_item(item, code_dir, venv_path):
    code = get_generated_vanilla_code(item)
    code_path = path.join(code_dir, "code.py")
    with open(code_path, "w") as f:
        f.write(code)
    tqdm.write("Running evaluation")
    cmd = [
        "docker",
        "run",
        "-it",
        "--rm",
        "--name",
        "dev_dataset_eval_item",
        "--read-only",
        "-v",
        f"{venv_path}:/venv",
        "--read-only",
        "-v",
        f"{code_path}:/code/code.py",
        "-w",
        "/code",
        "--cpus",
        "1",
        "--network",
        "none",
        DOCKER_IMAGE,
        "/venv/bin/python",
        "code.py",
    ]
    try:
        output, errors = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        ).communicate(timeout=60)
        stdout_text = output.decode()
        results = json.loads(stdout_text)
        r = ", ".join(map(str, results))
        tqdm.write(f"Test results: {r}")
        item["test_results"] = results
    except Exception as e:
        tqdm.write(f"Error: {e}")
        results = ["error", "error", "error"]
        item["test_results"] = results
        cmd = ["docker", "rm", "-f", "dev_dataset_eval_item"]
        subprocess.run(cmd)
    return results


def output_path(results):
    file_name = "copilot.json"
    return path.join(results, file_name)


async def main(args):
    venv_cache = args.venv_cache
    dataset = load_dataset(args.dataset)
    results = args.results
    if not os.path.exists(results):
        os.makedirs(results)

    for item in tqdm(dataset.items):
        code_dir = code_directory(item)
        if path.exists(code_dir):
            rmtree(code_dir)
        os.mkdir(code_dir)

        # venv_path = path.join(code_dir, "venv")
        # create_venv(venv_cache, venv_path, item)
        lsp = await create_copilot_lsp(code_dir)
        generated_without = await generate_item(item, lsp, code_dir)
        item["generated_code_vanilla"] = generated_without
        # eval_results_without = eval_item(item, code_dir, venv_path)
        # item["evaluated_code_vanilla"] = eval_results_without
        rmtree(code_dir)

    out_path = output_path(results)
    with open(out_path, "w") as f:
        f.write(json.dumps(dataset.items))


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-a", "--action", default="all", choices=["all", "generate", "eval"]
    )
    parser.add_argument("-d", "--dataset", required=True)
    parser.add_argument("-c", "--venv-cache", default="venv_cache")
    parser.add_argument("-r", "--results", default="results")

    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(main(parse_args()))
