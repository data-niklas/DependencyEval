from os import path
from dependency_eval.constants import INDENT, SALT

def get_requirements(item) -> str:
    requirements = item["package_dependencies"].copy()
    requirements_text = "\n".join(requirements)
    return requirements_text


def get_code_directory(base_directory, item) -> str:
    return path.join(base_directory, "eval_code_" + item["task_name"] + "_" + SALT)


def get_completion_code(item) -> str:
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


def get_generated_vanilla_code(item) -> str:
    return get_completion_code(item) + item["generated_code_vanilla"]


def get_generated_llm_lsp_code(item) -> str:
    return get_completion_code(item) + item["generated_code_llm_lsp"]
