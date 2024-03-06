from typing import List
import polars as pl

def lazy_filter_old_users(csv_file_path: str) -> List[str]:
    """Lazily return a list of all user names, which are older than 50. Read the users from `csv_file_path`. The name column is `name`, the age column is `age`."""
    df = pl.scan_csv(csv_file_path)
    names = df.filter(pl.col("age") > 50).select(pl.col("name")).collect()
    return names.to_series().to_list()