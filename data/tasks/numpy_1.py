import numpy as np
from typing import List

def add_strings_element_wise(a: List[str], b: List[str]) -> List[str]:
    """Add both lists of strings element-wise. Use the Numpy library.

    Args:
        a (List[str]): First list
        b (List[str]): Second list

    Returns:
        List[str]: Combined list
    """
    return np.strings.add(a, b)