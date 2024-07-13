from os import path

REQUIREMENTS_FILE = "__requirements__.txt"
LOG_FILE = path.abspath("generation_log.log")
INDENT = " " * 4
DOCKER_IMAGE = "python:3.7-slim-bullseye"
EVAL_PROMPT_FILE = path.join(path.dirname(__file__), "eval_prompt.py")
