from typing import Dict, Any
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    age: int

def convert_user_to_json(user: User) -> str:
    """Convert the given user model into a JSON string"""
    return user.model_dump_json()