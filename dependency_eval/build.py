import json
import re
from os import listdir, path

from dependency_eval import NAME, VERSION

LAST_FUNCTION_DEF_RE = re.compile(r"\ndef .+\(.*\).*:\n", re.MULTILINE)
IMPORT_RE = re.compile(
    r"((^|\n)from (.+) import (.+))|((^|\n)import (.+))", re.MULTILINE
)
DOC_RE = re.compile(r'"""((.|\n)+)"""', re.MULTILINE)
INIT_FILE = path.join(path.dirname(__file__), "__init__.py")


def content(file):
    with open(file, "r") as f:
        return f.read()


def split_solution(file):
    solution: str = content(file)
    matches = list(re.finditer(LAST_FUNCTION_DEF_RE, solution))

    last_match = matches[-1]
    before_function = solution[: last_match.start()]
    after_signature = solution[last_match.end() :]
    function_signature = last_match.group().strip("\n")

    matches = list(re.finditer(IMPORT_RE, before_function))
    imports = [m.group().strip("\n") for m in matches]
    context = before_function[matches[-1].end() :].strip("\n")

    matches = list(re.finditer(DOC_RE, after_signature))
    documentation = matches[0].group().strip("\n")
    solution = after_signature[matches[0].end() :].strip("\n")
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


def read_tasks(data_directory: str):
    solutions_directory = path.join(data_directory, "tasks")
    tests_directory = path.join(data_directory, "tests")
    tasks = []
    files = [
        file
        for file in listdir(solutions_directory)
        if path.isfile(path.join(solutions_directory, file)) and file.endswith(".py")
    ]
    for i, file in enumerate(files):
        filepath = path.join(solutions_directory, file)
        task_id = f"{NAME}_{i}"
        task_name = file[:-3]
        test_code = ""
        (
            import_statements,
            context,
            function_signature,
            function_documentation,
            solution,
        ) = split_solution(filepath)
        entry_point = function_signature[4:].split("(")[0]

        try:
            test_code = content(path.join(tests_directory, file))
        except:
            test_code = ""

        tasks.append(
            {
                "task_id": task_id,
                "task_name": task_name,
                "test_code": test_code,
                "import_statements": import_statements,
                "package_dependencies": [],
                "function_signature": function_signature,
                "function_documentation": function_documentation,
                "entry_point": entry_point,
                "context": context,
                "solution": solution,
            }
        )
    return tasks


def replace_version(new_version: str):
    with open(INIT_FILE, "r") as f:
        lines = f.readlines()
    patched_lines = [
        line if not line.startswith("VERSION =") else f'VERSION = "{new_version}"'
        for line in lines
    ]
    patched_init = "\n".join(patched_lines)
    with open(INIT_FILE, "w") as f:
        f.write(patched_init)


def build_dataset(data_directory: str, version: str):
    dataset_name = f"{NAME}_{version}.jsonl"
    metadata_file = path.join(data_directory, "metadata.json")
    metadata = json.loads(content(metadata_file))
    out_file = path.join(data_directory, "dist", dataset_name)
    tasks = read_tasks(data_directory)
    tasks = merge_metadata(tasks, metadata)
    with open(out_file, "w") as f:
        for item in tasks:
            f.write(json.dumps(item) + "\n")


def update_version(update_type: str):
    major, minor, patch = [int(value) for value in VERSION.split(".")]
    if update_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif update_type == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    new_version = f"{major}.{minor}.{patch}"
    return new_version
