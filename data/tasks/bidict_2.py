from bidict import bidict

def invert_bidict_direction(values: bidict) -> bidict:
    """Return the inverse of the given bidirectional mapping instance.

    Args:
        values (bidict): Bidirectional mapping between any keys and values

    Returns:
        bidict: Inverse of values
    """    
    return values.inverse