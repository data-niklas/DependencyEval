# from matplotlib import pyplot as plt
import json
import os
import sys
from collections import defaultdict
from functools import cmp_to_key
from os import path

from matplotlib import pyplot as plt
from sankeyflow import Sankey


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


def main():
    results_dir = sys.argv[1]
    if len(sys.argv) > 2:
        fi = lambda x: "codellama" in x
    else:
        fi = lambda x: True
    items = []
    for name in os.listdir(results_dir):
        print(name)
        if not name.endswith(".json") or not fi(name):
            continue
        with open(path.join(results_dir, name), "r") as f:
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
    print("{0:0.2f}".format(full_p))
    print("{0:0.2f}".format(partial_p))
    print("{0:0.2f}".format(none_p))
    print("{0:0.2f}".format(error_p))
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
    print("{0:0.2f}".format(full_p))
    print("{0:0.2f}".format(partial_p))
    print("{0:0.2f}".format(none_p))
    print("{0:0.2f}".format(error_p))
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
    print("{0:0.2f}".format(full_p))
    print("{0:0.2f}".format(partial_p))
    print("{0:0.2f}".format(none_p))
    print("{0:0.2f}".format(error_p))

    labels = ["full", "partial", "none", "error"]
    node_values = defaultdict(int)
    for k, v in flows.items():
        node_values[k[0]] += v
        node_values[k[1]] += v
    nodes = [
        [(l + "_in", node_values[l + "_in"], {"label": l}) for l in labels],
        [(l + "_out", node_values[l + "_out"], {"label": l}) for l in labels],
    ]
    plt.figure(figsize=(12, 8), dpi=144)
    s = Sankey(
        flows=[key + (value,) for (key, value) in flows.items()],
        nodes=nodes,
        cmap=plt.cm.Pastel1,
        flow_color_mode="source",
    )
    s.draw()
    plt.savefig("sankey.png")


if __name__ == "__main__":
    main()
