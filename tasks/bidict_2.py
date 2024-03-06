from bidict import bidict

def invert_bidict_direction(values: bidict) -> bidict:
    """Invert the position of keys and values in the bidict."""
    return values.inverse