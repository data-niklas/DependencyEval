from typing import Any, Callable, Dict, List

from tqdm import tqdm

from dependency_eval.models import Dataset, ModelConfiguration


def run_loop(
    model_configurations: List[ModelConfiguration],
    dataset: Dataset,
    model_configuration_finished_cb: Callable[[ModelConfiguration], None],
    item_cb: Callable[[ModelConfiguration, Dict[str, Any]], None],
    maybe_skip_model_configuration_cb: Callable[[ModelConfiguration], bool] = None
):
    for model_configuration in tqdm(model_configurations):
        tqdm.write(f"Running for {model_configuration.name}")
        if maybe_skip_model_configuration_cb is not None and maybe_skip_model_configuration_cb(model_configuration):
            tqdm.write(f"Skipping model configuration {model_configuration.name}")
            continue
        for item in tqdm(dataset.items):
            item_cb(model_configuration, item)
        model_configuration_finished_cb(model_configuration)
