from pydentic import BaseModel
from datetime import datetime
from typing import List


class UserAction(BaseModel):
    date: datetime
    input_text: str
    output_text: str
    cost: int


class User(BaseModel):
    id: int
    login: str
    balance: int
    actions: List[UserAction]
