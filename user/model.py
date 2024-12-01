from pydantic import BaseModel

# User Model
class User(BaseModel):
    username: str
    account: float