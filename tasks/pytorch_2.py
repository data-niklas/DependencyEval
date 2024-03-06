from numbers import Number
import torch

def create_1d_tensor_in_range(start: Number, end: Number) -> torch.Tensor:
    """Return a 1d tensor with values from start to end"""
    return torch.arange(start, end)