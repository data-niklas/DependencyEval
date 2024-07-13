from typing import Any

from dotted.collection import DottedList


def get_2d_board_entry(board: DottedList, index: str) -> Any:
    """Retrieve the value in the 2d board at the given index.

    Args:
        board (DottedList): A 2d dimensional board implemented through nested lists. The board may store any type of value.
        index (str): An index in the format of "column.row"

    Returns:
        Any: The value
    """
    return board[index]