# from matplotlib import pyplot as plt
import json
import os
import sys
from collections import defaultdict
from functools import cmp_to_key
from os import path

from dependency_eval.loader import load_dataset
from dependency_eval.models import KINDS, CODE_KINDS, MODIFICATION_KIND
from dependency_eval.venv_cache import get_venv_for_item, get_item_venv_cache_directory

import pygount
import tqdm


def lt_config(a, b):
    if "do_sample" not in a:
        a["do_sample"] = False
    if "do_sample" not in b:
        b["do_sample"] = False
    if "num_beams" in a and "num_beams" not in b:
        return False
    return a["do_sample"] < b["do_sample"]


def cmp(a, b):
    if a["model"] != b["model"]:
        return -1 if a["model"] < b["model"] else 1
    if a["config"] != b["config"]:
        return -1 if lt_config(a["config"], b["config"]) else 1
    return -1 if a["method"] < b["method"] else 1


def config_name(config):
    if "do_sample" in config and config["do_sample"] == True:
        return " °"  # + "{:.2f}".format(config["temperature"])
    else:
        return ""


def beam_name(config):
    if "num_beams" in config:
        return " |" + str(config["num_beams"])
    else:
        return ""


def find_column_names(items):
    names = []
    for i in items:
        name_splits = i["model"].split("/")
        model_base_name = (
            name_splits[1].split("-")[0] if len(name_splits) > 1 else name_splits[0]
        )
        base_name = (
            model_base_name
            + "METHOD"
            + config_name(i["config"])
            + beam_name(i["config"])
        )
        if "evaluated_code_vanilla" in i["items"][0]:
            names.append(base_name.replace("METHOD", ""))
        if "evaluated_code_llm_lsp" in i["items"][0]:
            names.append(base_name.replace("METHOD", " +lsp"))
    return names


def map_results(results):
    r = defaultdict(int)
    if results[0] == 0 and results[1] == 0:
        r["full"] = 1
    elif results[0] < results[2] and results[1] < results[2]:
        r["partial"] = 1
    elif results[0] == "error":
        r["error"] = 1
    else:
        r["none"] = 0
    return r


def get_result_stats(
    evaluation_results_directory: str, evaluation_results_filter: str = ""
):
    items = []
    for name in os.listdir(evaluation_results_directory):
        if not name.endswith(".json"):
            continue
        if evaluation_results_filter != "" and evaluation_results_filter not in name:
            continue
        with open(path.join(evaluation_results_directory, name), "r") as f:
            item = json.loads(f.read())
            items.append(item)

    items.sort(key=cmp_to_key(cmp))
    for item in items:
        item["items"].sort(key=lambda x: x["task_name"])
    row_names = [i["task_name"] for i in items[0]["items"]]
    column_names = find_column_names(items)
    rows = []
    flows = defaultdict(int)
    for j in range(len(row_names)):
        row = []
        for i in items:
            item = i["items"][j]
            if "evaluated_code_vanilla" in item:
                results = item["evaluated_code_vanilla"]
                t = map_results(results)
                row.append(t)
            if "evaluated_code_llm_lsp" in item:
                results = item["evaluated_code_llm_lsp"]
                t = map_results(results)
                t["lsp"] = 1
                row.append(t)
            if "evaluated_code_vanilla" in item and "evaluated_code_llm_lsp" in item:
                f_key = (
                    list(map_results(item["evaluated_code_vanilla"]).keys())[0] + "_in"
                )
                to_key = (
                    list(map_results(item["evaluated_code_llm_lsp"]).keys())[0] + "_out"
                )
                flows[(f_key, to_key)] += 1

        rows.append(row)
    return items, rows, row_names, flows


def show_result_stats(
    evaluation_results_directory: str, evaluation_results_filter: str = ""
):
    items, rows, row_names, _ = get_result_stats(
        evaluation_results_directory, evaluation_results_filter
    )
    total = len(items) * len(row_names) * 2
    full_total = sum([r["full"] for row in rows for r in row])
    partial_total = sum([r["partial"] for row in rows for r in row])
    error_total = sum([r["error"] for row in rows for r in row])
    none_total = total - full_total - partial_total - error_total
    full_p = full_total / total * 100
    partial_p = partial_total / total * 100
    error_p = error_total / total * 100
    none_p = none_total / total * 100
    print("All:")
    print("{0:0.2f} {1}".format(full_p, full_total))
    print("{0:0.2f} {1}".format(partial_p, partial_total))
    print("{0:0.2f} {1}".format(none_p, none_total))
    print("{0:0.2f} {1}".format(error_p, error_total))
    print("------")
    v_total = total / 2
    full_total = sum([r["full"] for row in rows for r in row if r["lsp"] == 0])
    partial_total = sum([r["partial"] for row in rows for r in row if r["lsp"] == 0])
    error_total = sum([r["error"] for row in rows for r in row if r["lsp"] == 0])
    none_total = v_total - full_total - partial_total - error_total
    full_p = full_total / v_total * 100
    partial_p = partial_total / v_total * 100
    error_p = error_total / v_total * 100
    none_p = none_total / v_total * 100
    print("No LLM_LSP:")
    print("{0:0.2f} {1}".format(full_p, full_total))
    print("{0:0.2f} {1}".format(partial_p, partial_total))
    print("{0:0.2f} {1}".format(none_p, none_total))
    print("{0:0.2f} {1}".format(error_p, error_total))
    print("------")
    v_total = total / 2
    full_total = sum([r["full"] for row in rows for r in row if r["lsp"] == 1])
    partial_total = sum([r["partial"] for row in rows for r in row if r["lsp"] == 1])
    error_total = sum([r["error"] for row in rows for r in row if r["lsp"] == 1])
    none_total = v_total - full_total - partial_total - error_total
    full_p = full_total / v_total * 100
    partial_p = partial_total / v_total * 100
    error_p = error_total / v_total * 100
    none_p = none_total / v_total * 100
    print("With LLM_LSP:")
    print("{0:0.2f} {1}".format(full_p, full_total))
    print("{0:0.2f} {1}".format(partial_p, partial_total))
    print("{0:0.2f} {1}".format(none_p, none_total))
    print("{0:0.2f} {1}".format(error_p, error_total))


def get_dataset_stats(dataset_file: str):
    dataset = load_dataset(dataset_file)
    total = len(dataset.items)
    task_groups = defaultdict(lambda: 0)
    kinds_count = defaultdict(lambda: 0)
    code_kinds_count = defaultdict(lambda: 0)
    modification_kinds_count = defaultdict(lambda: 0)
    python_version_count = defaultdict(lambda: 0)
    for item in dataset.items:
        task_group = item["task_name"].split("_")[0]
        task_groups[task_group] += 1
        kinds_count[item["kind"]] += 1
        code_kinds_count[item["code_kind"]] += 1
        python_version_count[item["python_version"]] += 1
        if "modification_kind" in item:
            modification_kinds_count[item["modification_kind"]] += 1
    task_groups = list(task_groups.items())
    task_groups.sort(key=lambda x: x[1], reverse=True)
    kinds_count = list(kinds_count.items())
    kinds_count.sort(key=lambda x: x[1], reverse=True)
    code_kinds_count = list(code_kinds_count.items())
    code_kinds_count.sort(key=lambda x: x[1], reverse=True)
    modification_kinds_count = list(modification_kinds_count.items())
    modification_kinds_count.sort(key=lambda x: x[1], reverse=True)
    python_version_count = list(python_version_count.items())
    python_version_count.sort(key=lambda x: x[1], reverse=True)

    dates = [item["date"] for item in dataset.items]
    dates.sort()

    return (
        dataset.name,
        total,
        task_groups,
        kinds_count,
        code_kinds_count,
        modification_kinds_count,
        dates,
        python_version_count,
    )


def show_dataset_stats(dataset_file: str):
    (
        dataset_name,
        total,
        task_groups,
        kinds_count,
        code_kinds_count,
        modification_kinds_count,
        dates,
        python_version_count,
    ) = get_dataset_stats(dataset_file)
    print(f"Showing stats for: '{dataset_name}' ({total} entries)")
    print("")
    print(f"The dataset has {len(task_groups)} unique task groups:")
    for task_group_name, task_group_count in task_groups:
        print(f"{task_group_name}: {task_group_count}")
    print("")
    print(f"The dataset has {len(kinds_count)} unique task kinds:")
    for kinds_name, kinds_count in kinds_count:
        print(f"{kinds_name}: {kinds_count}")
    print("")
    print(f"The dataset has {len(code_kinds_count)} unique code kinds:")
    for code_kinds_name, code_kinds_count in code_kinds_count:
        print(f"{code_kinds_name}: {code_kinds_count}")
    print("")
    modification_total_count = sum([x[1] for x in modification_kinds_count])
    print(
        f"The dataset has {len(modification_kinds_count)} (of {modification_total_count}) unique modification kinds:"
    )
    for modification_kinds_name, modification_kinds_count in modification_kinds_count:
        print(f"{modification_kinds_name}: {modification_kinds_count}")
    print("")
    print(f"The dataset uses {len(python_version_count)} unique Python versions:")
    for python_version, count in python_version_count:
        print(f"{python_version}: {count}")
    print("")
    print(
        f"The items span from {dates[0]} to {dates[-1]}, with a median of {dates[len(dates)//2]}"
    )


def show_all_results_stats(base_directory: str, filter: str):
    for directory in os.listdir(base_directory):
        result_dir = path.join(base_directory, directory)
        for file in os.listdir(result_dir):
            file_path = path.join(result_dir, file)
            if filter != "" and filter not in file_path:
                continue
            with open(file_path, "r") as f:
                results = json.loads(f.read())
                items = results["items"]
                w_set = set()
                wo_set = set()
                for v in items:
                    if "evaluated_code_llm_lsp" not in v or "evaluated_code_vanilla" not in v:
                        continue
                    if v["evaluated_code_llm_lsp"] == [0,0,2]:
                        w_set.add(v["task_name"])
                    if v["evaluated_code_vanilla"] == [0,0,2]:
                        wo_set.add(v["task_name"])
                wo_unique = wo_set - w_set
                w_unique = w_set - wo_set
                print(file_path.replace(base_directory + "/", "") + f"\nw: {len(w_set)} wo: {len(wo_set)} w - wo: {len(w_unique)} wo - w: {len(wo_unique)}")

def get_dependency_stats(item, venv_cache_directory):
    import logging
    logging.getLogger("pygount").setLevel("CRITICAL")
    get_venv_for_item(venv_cache_directory, None, item)
    venv_dir = get_item_venv_cache_directory(item, venv_cache_directory)
    lib_dir = path.join(venv_dir, "lib")
    site_packages_path = path.join(lib_dir, os.listdir(lib_dir)[0], "site-packages")
    dependency_dir = path.join(site_packages_path, item["package_name"])
    tqdm.tqdm.write(item["package_name"])

    with pygount.analysis.SourceScanner(
        iter([dependency_dir]), "py", pygount.common.regexes_from(pygount.analysis.DEFAULT_FOLDER_PATTERNS_TO_SKIP_TEXT), pygount.common.regexes_from(pygount.analysis.DEFAULT_NAME_PATTERNS_TO_SKIP_TEXT)
    ) as source_scanner:
        source_paths_and_groups_to_analyze = list(source_scanner.source_paths())
        duplicate_pool = pygount.analysis.DuplicatePool()
        from pygount.write import BaseWriter
        is_stdout = True
        with BaseWriter(None) as writer:
            for source_path, group in tqdm.tqdm(source_paths_and_groups_to_analyze):
                writer.add(
                    pygount.analysis.SourceAnalysis.from_file(
                        source_path,
                        group,
                        "automatic",
                        pygount.analysis.DEFAULT_FALLBACK_ENCODING,
                        generated_regexes=pygount.common.regexes_from(pygount.analysis.DEFAULT_GENERATED_PATTERNS_TEXT),
                        duplicate_pool=duplicate_pool,
                        merge_embedded_language=False,
                    )
                )
        return writer.project_summary.total_code_count, writer.project_summary.total_documentation_count


def show_dependencies_stats(dataset_file, venv_cache_directory, out_file):
    dataset = load_dataset(dataset_file)
    results = {}
    for item in tqdm.tqdm(dataset.items):
        if item["package_name"] in results:
            continue
        loc, documentation_percentage = get_dependency_stats(item, venv_cache_directory)
        results[item["package_name"]] = {
            "lines_of_code": loc,
            "lines_of_doc": documentation_percentage
        }
    with open(out_file, "w") as f:
        f.write(json.dumps(results))