from pydantic import BaseModel
# Product Model
class Product(BaseModel):
    name: str
    price: float
    quantity: int