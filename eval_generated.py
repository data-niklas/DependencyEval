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
CODE_FILE = path.join(CODE_DIR, "code.py")
VENV_DIR = path.join(CODE_DIR, "venv")
VENV_CACHE = path.join(path.dirname(__file__), ".venv_cache")

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
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print(e.output.decode())
            raise e
        os.remove(requirements_file)
    clone_virtualenv(cached_venv_dir, venv_dir)

def main():
    #llm_lsp_path = sys.argv[1]
    llm_lsp_path = "/nfs/home/nloeser_msc2023/llm-lsp"
    #dataset = sys.argv[2]
    dataset = "/scratch/students/nloeser_msc2023/dataset/DependencyEval_0.1.0_generated.jsonl"
    venv_cache = VENV_CACHE if len(sys.argv) < 4 else sys.argv[3]
    with open(dataset, "r") as f:
        items = [json.loads(i) for i in f.read().splitlines()]
    success = 0
    error = 0
    for item in tqdm(items):

        if path.exists(CODE_DIR):
            rmtree(CODE_DIR)
        os.mkdir(CODE_DIR)
        requirements = item["package_dependencies"].copy()
        requirements.append(llm_lsp_path)
        tqdm.write("Creating venv")
        create_venv(VENV_DIR, requirements, venv_cache)
        code = item["generated_code"] + "\n\n" + item["test_code"]
        with open(CODE_FILE, "w") as f:
            f.write(code)
        tqdm.write("Running generation")
        cmd = [f"{VENV_DIR}/bin/python", CODE_FILE]
        try:
            output, errors = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).communicate(timeout=60)
            stdout_text = output.decode()
            results = json.loads(stdout_text)
            r = ", ".join(results)
            tqdm.write(f"Test results: {r}")
            item["test_results"] = results
            if len(results[0]) > 0 or len(results[1]) > 0:
                error += 1
            else:
                success += 1
        except Exception:
            results = ["error", "error", "error"]
            item["test_results"] = results
            error += 1
        rmtree(CODE_DIR)
    with open(dataset.replace(".jsonl", "_tested.jsonl"), "w") as f:
        f.write("\n".join([json.dumps(i) for i in items]))
    with open(dataset.replace(".jsonl", "_tested.metrics"), "w") as f:
        f.write("\n".join(["Success: " + str(success), "Error: " + str(error)]))

        

if __name__ == "__main__":
    main()