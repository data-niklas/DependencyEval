from sklearn.preprocessing import OneHotEncoder

def create_dense_one_hot_encoder() -> OneHotEncoder:
    """Create a OneHotEncoder which encodes categorical features into a dense matrix.

    Returns:
        OneHotEncoder: New instance of OneHotEncoder encoding categorical features into a dense matrix
    """    
    return OneHotEncoder(sparse_output=False)