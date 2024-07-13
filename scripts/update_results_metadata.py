import json
from argparse import ArgumentParser
from os import listdir, path


def main(args):
    with open(args.metadata, "r") as f:
        items = json.loads(f.read())
        metadata = {item["task_name"]: item for item in items}
    # with open(args.results, "r") as f:
    #     t = [json.loads(line) for line in f.read().splitlines()]
    # for item in t:
    #     mi = metadata[item["task_name"]]
    #     for k, v in mi.items():
    #         item[k] = v
    # with open(args.results, "w") as f:
    #     f.write("\n".join([json.dumps(i) for i in t]))

    for p in listdir(args.results):
        p = path.join(args.results, p)
        with open(p, "r") as f:
            item = json.loads(f.read())
        for i in item["items"]:
            mi = metadata[i["task_name"]]
            for k, v in mi.items():
                i[k] = v
        with open(p, "w") as f:
            f.write(json.dumps(item))


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-r", "--results", default="dataset/results")
    parser.add_argument("-m", "--metadata")
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
