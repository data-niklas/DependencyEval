from typing import Any, Dict

from bidict import OnDup, OnDupAction, bidict


def insert_values_drop_old_on_dup(values: bidict, items: Dict[str, Any]):
    """Insert all key value pairs from items into values at once. Drop old keys and values on duplication.

    Args:
        values (bidict): Bidirectional mapping between keys and values
        items (Dict[str, Any]): Python mapping between keys and values to be inserted into values
    """    
    values.putall(items, OnDup(key=OnDupAction.DROP_OLD, val=OnDupAction.DROP_OLD))