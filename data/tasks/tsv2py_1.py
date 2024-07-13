from datetime import datetime
from typing import Any, List, Tuple

from tsv.helper import Parser


def parse_tsv_file(filename: str) -> List[Tuple[Any, ...]]:
    """The file at filepath contains entries in the tsv format. Parse the file into a Python list of tuples.

    Args:
        filename (str): Name of the TSV file. The TSV entries have the following columns: name, age, birthday

    Returns:
        List[Tuple[Any, ...]]: List of Python tuples of the tabular data
    """
    parser = Parser(fields=(str, int, datetime))
    with open(filename, "rb") as f:
        return parser.parse_file(f)