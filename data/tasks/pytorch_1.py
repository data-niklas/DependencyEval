from torch.nn import CrossEntropyLoss

def create_sum_cross_entropy_loss_module() -> CrossEntropyLoss:
    """Create an instance of CrossEntropyLoss which computes the sum of the cross entropy loss.

    Returns:
        CrossEntropyLoss: New instance which computes the sum of the cross entropy loss 
    """    
    return CrossEntropyLoss(reduction="sum")