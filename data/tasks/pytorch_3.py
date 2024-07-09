import torch

def calculate_cholesky(input: torch.Tensor) -> torch.Tensor:
    """Calculate the Cholesky decomposition.

    Args:
        input (torch.Tensor): Input tensor

    Returns:
        torch.Tensor: Cholesky decomposition of input tensor
    """    
    return torch.linalg.cholesky(input)