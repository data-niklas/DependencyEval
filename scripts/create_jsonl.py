from os import path
from os import listdir
import re
from logzero import logger
import json
import sys

SCRIPTS_DIR = path.dirname(__file__)
DATA_DIR = path.join(path.dirname(SCRIPTS_DIR), "data")
SOLUTIONS_DIR = path.join(DATA_DIR, "tasks")
TESTS_DIR = path.join(DATA_DIR, "tests")
METADATA_FILE = path.join(DATA_DIR, "metadata.json")
METADATA = json.load(open(METADATA_FILE, "r"))
DIST_DIR = path.join(DATA_DIR, "dist")

NAME = "DependencyEval"
VERSION = "0.2.1"

OUT = path.join(DIST_DIR, f"DependencyEval_{VERSION}.jsonl")

LAST_FUNCTION_DEF_RE = re.compile(r"\ndef .+\(.*\).*:\n", re.MULTILINE)
IMPORT_RE = re.compile(r"((^|\n)from (.+) import (.+))|((^|\n)import (.+))", re.MULTILINE)
DOC_RE = re.compile(r'"""((.|\n)+)"""', re.MULTILINE)

def content(file):
    with open(file, "r") as f:
        return f.read()

def split_solution(file):
    solution: str = content(file)
    matches = list(re.finditer(LAST_FUNCTION_DEF_RE, solution))

    last_match = matches[-1]
    before_function = solution[:last_match.start()]
    after_signature = solution[last_match.end():]
    function_signature = last_match.group().strip("\n")

    matches = list(re.finditer(IMPORT_RE, before_function))
    imports = [m.group().strip("\n") for m in matches]
    context = before_function[matches[-1].end():].strip("\n")

    matches = list(re.finditer(DOC_RE, after_signature))
    documentation = matches[0].group().strip("\n")
    solution = after_signature[matches[0].end():].strip("\n")
    return imports, context, function_signature, documentation, solution

def merge_metadata(tasks, metadata):
    tasks.sort(key=lambda x: x["task_name"])
    metadata.sort(key=lambda x: x["task_name"])
    assert len(tasks) == len(metadata)
    new_tasks = []
    for a, b in zip(tasks, metadata):
        assert a["task_name"] == b["task_name"]
        new_tasks.append({**a, **b})
    new_tasks.sort(key=lambda x: x["task_id"])
    return new_tasks

def read_tasks():
    tasks = []
    files = [file for file in listdir(SOLUTIONS_DIR) if path.isfile(path.join(SOLUTIONS_DIR, file)) and file.endswith(".py")]
    for i, file in enumerate(files):
        filepath = path.join(SOLUTIONS_DIR, file)
        task_id = f"{NAME}_{i}"
        task_name = file[:-3]
        test_code = ""
        import_statements, context, function_signature, function_documentation, solution = split_solution(filepath)
        entry_point = function_signature[4:].split("(")[0]
        
        try:
            test_code = content(path.join(TESTS_DIR, file))
        except:
            test_code = ""

        tasks.append({
            "task_id": task_id,
            "task_name": task_name,
            "test_code": test_code,
            "import_statements": import_statements,
            "package_dependencies": [],
            "function_signature": function_signature,
            "function_documentation": function_documentation,
            "entry_point": entry_point,
            "context": context,
            "solution": solution
        })
    return tasks

def main():
    tasks = read_tasks()
    tasks = merge_metadata(tasks, METADATA)
    with open(OUT, "w") as f:
        for item in tasks:
            f.write(json.dumps(item) + "\n")


if __name__ == "__main__":
    main()