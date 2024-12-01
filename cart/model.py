from pydantic import BaseModel
from typing import List

# Cart Item Model
class CartItem(BaseModel):
    username: str
    productID: str
    status: str
    quantity: int

