from fastapi import APIRouter
from model import Product
from typing import List
import service

router = APIRouter()

# GET all products
@router.get("/products")
async def getProducts():
    return await service.getProducts()

# GET a product by id
@router.get("/products/{productID}")
async def getProduct(productID):
    return await service.getProduct(productID)

# POST new product
@router.post("/products")
async def addProduct(product: Product):
    return await service.postProduct(product)

# PUT update product
@router.put("/products/{productID}")
async def putProduct(productID: str, product: Product):
    return await service.putProduct(productID, product)

# PUT increase quantity of product
@router.put("/products/{productID}/increase")
async def increaseProductQuantity(productID: str, amount: int):
    return await service.increaseProductQuanlity(productID, amount)

# PUT decrease quantity of product
@router.put("/products/{productID}/decrease")
async def decreaseProductQuantity(productID: str, amount: int):
    print(productID, amount)
    return await service.decreaseProductQuanlity(productID, amount)

# DELETE product
@router.delete("/products/{productID}")
async def deleteProduct(productID: str):
    return await service.deleteProduct(productID)