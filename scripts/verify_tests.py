from argparse import ArgumentParser
from os import listdir


def main(args):
    for task_name in listdir(args.tests):
        pass


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--tests")
    parser.add_argument("--tasks")
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
