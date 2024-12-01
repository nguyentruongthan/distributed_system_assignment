from fastapi import APIRouter
from model import User
from typing import List
import service

router = APIRouter()

# GET all users
@router.get("/users")
async def getUsers():
    return await service.getUsers()

# GET a user by username
@router.get("/users/{username}")
async def getUser(username):
    return await service.getUser(username)

# POST new user
@router.post("/users")
async def addUser(username: str):
    return await service.postUser(username)

# PUT increase user account
@router.put("/users/{username}/increase/{amount}")
async def increaseUserAccount(username: str, amount: int):
    return await service.increaseUserAccount(username, amount)

# PUT decrease user account
@router.put("/users/{username}/decrease/{amount}")
async def decreaseUserAccount(username: str, amount: int):
    return await service.decreaseUserAccount(username, amount)

# DELETE product
@router.delete("/users/{username}")
async def deleteUser(username: str):
    return await service.deleteUser(username)