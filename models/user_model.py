from pydantic import BaseModel
from datetime import datetime


class UserAction(BaseModel):
    date: datetime
    input_text: str
    output_text: str
    cost: int


class User(BaseModel):
    id: int
    login: str
    balance: int

class UserBase(BaseModel):
    login: str

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class ActionBase(BaseModel):
    input_text: str
    output_text: str
    cost: int

class PredictionRequest(BaseModel):
    input_text: str
    min_len: int
    max_len: int
