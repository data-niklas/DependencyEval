import json
import os
from os import path
from typing import List

from dependency_eval.models import (
    Dataset,
    ModelConfiguration,
    ModelConfigurationGeneration,
)


def read_model_configurations(directory):
    configurations = []
    for file_name in os.listdir(directory):
        if not file_name.endswith(".json"):
            continue
        file_path = path.join(directory, file_name)
        with open(file_path, "r") as f:
            config = json.loads(f.read())
        configurations.append(
            ModelConfiguration(
                model=config["model"], config=config["config"], name=file_name[:-5]
            )
        )
    return configurations


def read_generation_results(directory) -> List[ModelConfigurationGeneration]:
    configurations = []
    for file_name in os.listdir(directory):
        if not file_name.endswith(".json"):
            continue
        file_path = path.join(directory, file_name)
        with open(file_path, "r") as f:
            config = json.loads(f.read())
        configurations.append(
            ModelConfigurationGeneration(
                model=config["model"],
                config=config["config"],
                name=config["name"],
                items=config["items"],
            )
        )
    return configurations


def load_dataset(dataset_path) -> Dataset:
    with open(dataset_path, "r") as f:
        items = [json.loads(i) for i in f.read().splitlines()]
    return Dataset(name=path.basename(dataset_path)[:-6], items=items)
