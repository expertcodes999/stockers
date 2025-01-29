
from pydantic import BaseModel
from typing import List

class PayoutBase(BaseModel):
    country: str
    amount: float