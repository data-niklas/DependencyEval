import pandas as pd

def get_first_group_entry_allow_na(grouped_df: pd.core.groupby.GroupBy) -> pd.core.generic.NDFrameT:
    """Return the first row for each group, while not skipping NA values.

    Args:
        grouped_df (pd.core.groupby.GroupBy): The already grouped data frame.

    Returns:
        pd.core.generic.NDFrameT: A generic multi dimensional dataframe, containing each first row result.
    """
    return grouped_df.first(skipna=False)