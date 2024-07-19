import os
import subprocess
from hashlib import sha256
from os import path
from typing import Optional
from venv import EnvBuilder

from clonevirtualenv import clone_virtualenv
from tqdm import tqdm

from dependency_eval.constants import REQUIREMENTS_FILE
from dependency_eval.dataset_utils import get_requirements


def hash(text: str) -> str:
    return sha256(text.encode()).hexdigest()


def create_venv(venv_directory: str, requirements: str):
    tqdm.write("Creating new venv in cache")
    builder = EnvBuilder(
        system_site_packages=False,
        clear=False,
        symlinks=False,  # Important for the Docker container!
        upgrade=False,
        with_pip=True,
        prompt=None,
        upgrade_deps=False,
    )
    builder.create(venv_directory)
    context = builder.ensure_directories(venv_directory)
    with open(REQUIREMENTS_FILE, "w") as f:
        f.write(requirements)
    cmd = [context.env_exec_cmd, "-m", "pip", "install", "packaging", "wheel"]
    subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    cmd = [context.env_exec_cmd, "-m", "pip", "install", "-r", REQUIREMENTS_FILE]
    subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    os.remove(REQUIREMENTS_FILE)


def get_venv(
    venv_cache_directory: str, venv_directory: Optional[str], requirements: str
):
    requirement_items = requirements.split("\n")
    requirement_items.sort()
    requirements = "\n".join(requirement_items)
    requirements_hash = hash(requirements)
    if not path.exists(venv_cache_directory):
        os.makedirs(venv_cache_directory)

    cached_venv_directory = path.join(venv_cache_directory, requirements_hash)
    if not path.exists(cached_venv_directory):
        create_venv(cached_venv_directory, requirements)
    if venv_directory is not None:
        clone_virtualenv(cached_venv_directory, venv_directory)


def get_venv_for_item(
    venv_cache_directory: str, venv_directory: Optional[str], llm_lsp_directory, item
):
    path.abspath(llm_lsp_directory)
    requirements = get_requirements(item)
    requirements += "\n-e " + llm_lsp_directory
    get_venv(venv_cache_directory, venv_directory, requirements)
