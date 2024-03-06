from typing import List, Tuple, Any
from datetime import datetime
from tsv.helper import Parser

def parse_tsv_file(filename: str) -> List[Tuple[Any, ...]]:
    """The file at filepath contains entries in the tsv format. Parse the file into a Python list of tuples. The content has the following columns: name, age, birthday"""
    parser = Parser(fields=(str, int, datetime))
    with open(filename, "rb") as f:
        return parser.parse_file(f)