from sqlalchemy import Row
from sqlalchemy.engine.row import _TP


def get_tuple_of_row(row: Row) -> _TP:
    """Return this row as a tuple.

    Args:
        row (Row): Input row

    Returns:
        _TP: Input row represented as a tuple
    """    
    return row._tuple()