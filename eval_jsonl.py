import sys
import json
from os import path
import os
import subprocess
from venv import EnvBuilder
from shutil import rmtree
from tqdm import tqdm
from hashlib import sha256
from clonevirtualenv import clone_virtualenv

CODE_DIR = path.join(path.dirname(__file__), "eval_code")
EVAL_PROMPT = path.join(path.dirname(__file__), "eval_prompt.py")
CODE_FILE = path.join(CODE_DIR, "code.py")
VENV_DIR = path.join(CODE_DIR, "venv")
VENV_CACHE = path.join(path.dirname(__file__), ".venv_cache")

def main():
    llm_lsp_path = sys.argv[1]
    file = sys.argv[2]
    venv_cache = VENV_CACHE if len(sys.argv) < 4 else sys.argv[3]
    with open(file, "r") as f:
        items = [json.loads(i) for i in f.read().splitlines()]
    for item in tqdm(items):
        if path.exists(CODE_DIR):
            rmtree(CODE_DIR)
        os.mkdir(CODE_DIR)
        requirements = item["package_dependencies"].copy()
        requirements.append(llm_lsp_path)
        tqdm.write("Creating venv")
        create_venv(VENV_DIR, requirements, venv_cache)
        code = "\n".join(item["import_statements"]) + "\n\n"
        if item["context"] != "":
            code += item["context"] + "\n\n"
        code += item["function_signature"] + "\n  " + item["function_documentation"] + "\n"
        
        with open(CODE_FILE, "w") as f:
            f.write(code)
        tqdm.write("Running generation")
        cmd = [f"{VENV_DIR}/bin/python", EVAL_PROMPT, CODE_FILE]
        output, error = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()
        generated = output.decode()
        tqdm.write(f"Generated: {generated}")
        item["generated_code"] = generated
        rmtree(CODE_DIR)
    with open(file.replace(".jsonl", "_generated.jsonl"), "w") as f:
        f.write("\n".join([json.dumps(i) for i in items]))

    

def create_venv(venv_dir, requirements, venv_cache):
    requirements_text = "\n".join(requirements)
    requirements_hash = sha256(requirements_text.encode()).hexdigest()
    if not path.exists(venv_cache):
        os.makedirs(venv_cache)
    cached_venv_dir = path.join(venv_cache, requirements_hash)
    if not path.exists(cached_venv_dir):
        tqdm.write("Creating new venv in cache")
        builder = EnvBuilder(system_site_packages=False,
                                clear=False,
                                symlinks=True,
                                upgrade=False,
                                with_pip=True,
                                prompt=None,
                                upgrade_deps=False)
        builder.create(cached_venv_dir)
        context = builder.ensure_directories(cached_venv_dir)
        requirements_file = "__requirements__.txt"
        with open(requirements_file, "w") as f:
            f.write(requirements_text)
        cmd = [context.env_exec_cmd, '-m', 'pip', 'install', '-r', requirements_file]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        os.remove(requirements_file)
    clone_virtualenv(cached_venv_dir, venv_dir)


if __name__ == "__main__":
    main()