import json
import os
from argparse import ArgumentParser
from os import path

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


def main(args):
    if not path.exists(args.directory):
        os.makedirs(args.directory)
    with open(args.file, "r") as f:
        result = json.loads(f.read())
    for item in result["items"]:
        if "generated_code_vanilla" in item:
            name = item["task_name"] + "_vanilla.py"
            item_path = path.join(args.directory, name)
            with open(item_path, "w") as f:
                f.write(get_generated_vanilla_code(item))
        if "generated_code_llm_lsp" in item:
            name = item["task_name"] + "_llm_lsp.py"
            item_path = path.join(args.directory, name)
            with open(item_path, "w") as f:
                f.write(get_generated_llm_lsp_code(item))


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-f", "--file")
    parser.add_argument("-d", "--directory")
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
