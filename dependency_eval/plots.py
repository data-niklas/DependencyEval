from collections import defaultdict

from matplotlib import pyplot as plt
from sankeyflow import Sankey

from dependency_eval.stats import get_stats


def plot_stats(evaluation_results_directory: str, plot_file: str):
    _, _, _, flows = get_stats(evaluation_results_directory)
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
