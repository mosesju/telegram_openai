# app/models.py

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class Message(BaseModel):
    role: str
    content: str

class ModelName(str, Enum):
    gpt_3 = "gpt-3.5-turbo-1106"
    gpt_4 = "gpt-4-1106-preview"
    # You can add more models as needed

class Item(BaseModel):
    query: str
    messages: List[Message]
    k: int = 5

class SupabaseInteraction(BaseModel):
    user_name: Optional[str] =None
    user_input: str
    response: str
    vector: Optional[List[float]] = None