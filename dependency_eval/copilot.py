from dependency_eval.dataset_utils import get_completion_code
from pygls.lsp.client import BaseLanguageClient
from lsprotocol.types import *
from os import path
import subprocess
from dependency_eval.constants import COPILOT_NODE_SERVER_REPOSITORY
import time
from logzero import logger


def ensure_copilot_node_server(copilot_node_server_directory: str):
    if path.exists(copilot_node_server_directory):
        logger.debug("Copilot node server directory already exists")
        return
    command = [
        "git",
        "clone",
        COPILOT_NODE_SERVER_REPOSITORY,
        copilot_node_server_directory,
    ]
    output, errors = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    ).communicate(timeout=120)
    logger.debug("Done cloning copilot node server repository")


async def create_copilot_lsp(code_dir, copilot_node_server_dir):
    lsp: BaseLanguageClient = BaseLanguageClient("copilot", "1.0.0")
    await lsp.start_io(
        "node",
        path.join(copilot_node_server_dir, "copilot", "dist", "language-server.js"),
        "--stdio",
    )

    @lsp.feature("workspace/configuration")
    def configuration(ls, params):
        pass

    @lsp.feature("window/logMessage")
    def configuration(ls, params):
        pass

    @lsp.feature("textDocument/publishDiagnostics")
    def diagnostics(ls, params):
        pass

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


def char_line_of_code(code):
    if code == "":
        return 0, 0
    lines = code.splitlines()
    last_line_index = len(lines) - 1
    last_line = lines[last_line_index]
    last_char_index = len(last_line)
    return max(last_char_index, 0), max(last_line_index, 0)


async def generate_item_with_copilot(item, lsp, code_dir):
    start_time = time.time()
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
    end_time = time.time()
    return generated, end_time - start_time
