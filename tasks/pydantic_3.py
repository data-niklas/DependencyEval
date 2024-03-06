from typing import Dict, Any
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    age: int

def duplicate_user(user: User) -> User:
    """Return a copy of the user"""
    return user.model_copy()