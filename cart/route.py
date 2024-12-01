from fastapi import APIRouter
from model import CartItem
from typing import List
import service

router = APIRouter()

# GET user's cart
@router.get("/cart/{username}")
async def getCart(username: str):
    return await service.getCart(username)

# POST add item to cart
@router.post("/cart/{username}/add")
async def addToCart(username: str, productID: str, quantity: int):
    return await service.addToCart(username, productID, quantity)

# PUT update item quantity in cart
@router.put("/cart/{username}/update")
async def updateCart(username: str, productID: str, quanlity: int):
    return await service.updateCart(username, productID, quanlity)

# DELETE remove item from cart
@router.delete("/cart/{username}/remove/{productID}")
async def removeFromCart(username: str, productID: str):
    return await service.removeFromCart(username, productID)

# POST payment for items in cart
@router.post("/cart/{username}/checkout")
async def checkoutCart(username: str):
    return await service.checkoutCart(username)