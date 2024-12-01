from database import productCollection
from model import Product
from fastapi import HTTPException
from bson import ObjectId
from schema import listSerial, individualSerial
from kafka_producer import producer
import config, define
import json 
from kafka_consumer import kafkaMessages

async def getProducts():
    return listSerial(productCollection.find())

async def getProduct(productID: str):
    return individualSerial(productCollection.find_one({"_id": ObjectId(productID)}))

async def postProduct(product: Product):
    newProduct = productCollection.insert_one(product.model_dump())
    if not newProduct.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to add product")
    return {"message": "Product added successfully"}

async def putProduct(productID: str, product: Product):
    if not ObjectId.is_valid(productID):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    updatedProduct = productCollection.find_one_and_update(
        {"_id": ObjectId(productID)},
        {"$set": product.model_dump()},
        return_document=True
    )
    if not updatedProduct:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product updated successfully"}

async def deleteProduct(productID: str):
    if not ObjectId.is_valid(productID):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    deletedProduct = productCollection.find_one_and_delete({"_id": ObjectId(productID)})
    if not deletedProduct:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# Increase quantity of product
async def increaseProductQuanlity(productID: str, amount: int):
    if not ObjectId.is_valid(productID):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    updatedProduct = productCollection.find_one_and_update(
        {"_id": ObjectId(productID)},
        {"$inc": {"quantity": amount}},  # Increment the 'quantity' field by 'amount'
        return_document=True
    )
    
    if not updatedProduct:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": f"Product quantity increased by {amount}", "product": individualSerial(updatedProduct)}

# Decrease quantity of product
async def decreaseProductQuanlity(productID: str, amount: int):
    if not ObjectId.is_valid(productID):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    product = productCollection.find_one({"_id": ObjectId(productID)})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    current_quantity = product.get("quantity", 0)
    
    # Check if there is enough quantity to decrease
    if current_quantity < amount:
        raise HTTPException(status_code=400, detail="Insufficient product quantity")
    
    updatedProduct = productCollection.find_one_and_update(
        {"_id": ObjectId(productID)},
        {"$inc": {"quantity": -amount}},  # Decrement the 'quantity' field by 'amount'
        return_document=True
    )
    
    if not updatedProduct:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": f"Product quantity decreased by {amount}", "product": individualSerial(updatedProduct)}

async def checkoutCart(data: dict):
    """
    {
        "id": f"c{checkoutCartID}",
        "opcode": OP_CHECKOUT_CART,
        "username": username,
        "items":
            [
                {
                    "productID": productID,
                    "quantity": quantity
                },
                ...
                {
                    "productID": productID,
                    "quantity": quantity
                },
            ]
    }
    """
    print("checkout cart")

    items: list[dict] = data["items"]

    totalPrice = 0
    invalidProducts = []
    notEnoughQuantityProducts = []

    for item in items:
        product: dict = await getProduct(item["productID"])
        
        # Check product is invalid
        if not product: invalidProducts.append(item)
        else:
            # Check quantity valid of product
            if item["quantity"] > product["quantity"]:
                notEnoughQuantityProducts.append(item)
            else:
                totalPrice += item["quantity"] * product["price"]

    if invalidProducts:
        # Send faild to kafka broker
        data["opcode"] = define.OP_CHECK_PRODUCT_QUANTITY_FAILED
        data["invalidProducts"] = invalidProducts

        producer.send(config.KAFKA_TOPIC, json.dumps(data).encode("utf-8"))
        print(f"Products: {invalidProducts} are invalid")
        return
    
    if notEnoughQuantityProducts:
        data["opcode"] = define.OP_CHECK_PRODUCT_QUANTITY_FAILED
        data["notEnoughQuantityProducts"] = notEnoughQuantityProducts

        producer.send(config.KAFKA_TOPIC, json.dumps(data).encode("utf-8"))
        print(f"Products: {notEnoughQuantityProducts} is not enough quantity in inventory")
        return
    
    # Increase product quantity
    for item in items:
        await decreaseProductQuanlity(item["productID"], item["quantity"])

    data["opcode"] = define.OP_CHECK_PRODUCT_QUANTITY_SUCCESS
    data["totalPrice"] = totalPrice
    producer.send(config.KAFKA_TOPIC, json.dumps(data).encode("utf-8"))
    print(data)


async def restoreProduct(msg_json: dict):
    """
    {
        "id": f"c{checkoutCartID}",
        "opcode": OP_CHECK_USER_ACCOUNT_FAILED,
        "username": username,
        "items":
        [
            {
                "productID": productID,
                "quantity": quantity
            },
            ...
            {
                "productID": productID,
                "quantity": quantity
            },
        ],
        ...
    }
    """
    items: list[dict] = msg_json["items"]
    for item in items:
        await increaseProductQuanlity(item["productID"], item["quantity"])

