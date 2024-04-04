from typing import Dict, Any
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    age: int

def duplicate_user(user: User) -> User:
    """Duplicate the user.

    Args:
        user (User): The Pydantic user model

    Returns:
        User: Deep copy of the user
    """    
    return user.model_copy()