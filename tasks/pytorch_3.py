import torch

def calculate_cholesky(input: torch.Tensor) -> torch.Tensor:
    """Calculate the Cholesky decomposition of input."""
    return torch.linalg.cholesky(input)