#from matplotlib import pyplot as plt
import sys
from os import path
import os
import json
from functools import cmp_to_key

from textual.app import App, ComposeResult
from textual.widgets import DataTable

class TableApp(App):
    def __init__(self, columns, rows):
        super().__init__()
        self.rows = rows
        self.columns = columns

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*self.columns)
        table.add_rows(self.rows)
        table.zebra_stripes = True
        table.fixed_columns = 1

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
        return " °" + "{:.2f}".format(config["temperature"])
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
        model_base_name = name_splits[1].split("-")[0] if len(name_splits) > 1 else name_splits[0]
        base_name = model_base_name + "METHOD" + config_name(i["config"]) + beam_name(i["config"])
        if "evaluated_code_vanilla" in i["items"][0]:
            names.append(base_name.replace("METHOD", ""))
        if "evaluated_code_llm_lsp" in i["items"][0]:
            names.append(base_name.replace("METHOD", " +lsp"))
    return names

def main():
    results_dir = sys.argv[1]
    items = []
    for name in os.listdir(results_dir):
        if not name.endswith(".json"):
            continue
        with open(path.join(results_dir, name), "r") as f:
            item = json.loads(f.read())
            items.append(item)
    
    items.sort(key=cmp_to_key(cmp))
    for item in items:
        item["items"].sort(key=lambda x: x["task_name"])
    row_names = [i["task_name"] for i in items[0]["items"]]
    column_names = find_column_names(items)
    text = []
    for j in range(len(row_names)):
        row = []
        for i in items:
            item = i["items"][j]
            if "evaluated_code_vanilla" in item:
                results = item["evaluated_code_vanilla"]
                t = "+" if results[0] == 0 and results[1] == 0 else "~" if results[0] < results[2] and results[1] < results[2] else ""
                row.append(t)
            if "evaluated_code_llm_lsp" in item:
                results = item["evaluated_code_llm_lsp"]
                t = "+" if results[0] == 0 and results[1] == 0 else "~" if results[0] < results[2] and results[1] < results[2] else ""
                row.append(t)
        text.append(row)

    for row, name in zip(text, row_names):
        row.insert(0, name)
    app = TableApp([""] + column_names, text)
    app.run()
    #plt.table(cellText=text,rowLabels=row_names,colLabels=column_names, loc="center")
    #plt.savefig("plot.png")


if __name__ == "__main__":
    main()