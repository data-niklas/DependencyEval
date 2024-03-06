from typing import Dict, Any
from bidict import bidict, OnDup, OnDupAction

def insert_values_drop_old_on_dup(values: bidict, items: Dict[str, Any]):
    """Insert all key value pairs from items into values. Drop old keys and values on duplication."""    
    values.putall(items, OnDup(key=OnDupAction.DROP_OLD, val=OnDupAction.DROP_OLD))