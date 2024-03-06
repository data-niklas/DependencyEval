from sqlalchemy import Row
from sqlalchemy.engine.row import _TP

def get_tuple_of_row(row: Row) -> _TP:
    """Return a tuple of this row"""
    return row._tuple()