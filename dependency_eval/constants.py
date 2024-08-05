from os import path
from uuid import uuid4

SALT = str(uuid4())[:8]

REQUIREMENTS_FILE = f"__requirements__{SALT}.txt"
LOG_FILE = path.abspath(f"generation_log_{SALT}.log")
INDENT = " " * 4
DOCKER_IMAGE = "python:3.7-slim-bullseye"
EVAL_PROMPT_FILE = path.join(path.dirname(__file__), "eval_prompt.py")
