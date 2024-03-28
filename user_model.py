from pydentic import BaseModel
from datetime import datetime
from typing import List


class UserAction(BaseModel):
    date: datetime
    input_text: str
    output_text: str


class UserWallet:
    def __init__(self, id: int, balance: int):
        self.__id = id
        self.__balance = balance

    def check_balance(self) -> int:
        """Returns the user's balance"""
        pass

    def reduce_balance(self, num: int):
        """This method implements logic when the user spends his coins. It reduces the user's balance in the DB"""
        pass

    def top_up_balance(self, num: int):
        """Top the user's balance up on num coins"""
        pass


class UserHystory:
    def __init__(self, id: int):
        self.__id = id
    
    def check_hystory(self, num_elements: int) -> List[UserAction]:
        """Returns num_elements number of the user's actions"""
        pass


class User(BaseModel):
    id: int
    login: str
    wallet: UserWallet
    actions: UserHystory
