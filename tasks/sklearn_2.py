from sklearn.preprocessing import OneHotEncoder

def create_polars_compatible_one_hot_encoder() -> OneHotEncoder:
    """Create a OneHotEncoder which encodes categorical features into polars containers."""
    encoder = OneHotEncoder()
    encoder.set_output("polars")
    return encoder