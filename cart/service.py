import json
from fastapi import HTTPException
from bson import ObjectId
import asyncio

from database import cartCollection
from model import CartItem
from schema import listSerial, individualSerial
from kafka_producer import producer
import config, define
from kafka_consumer import kafkaMessages

checkoutCartID = 0

# GET user's cart
async def getCart(username: str):
    return listSerial(cartCollection.find({"username": username}))

# POST add item to cart
async def addToCart(username: str, productID: str, quantity: int):
    if not ObjectId.is_valid(productID):
        raise HTTPException(status_code=400, detail="Invalid product ID")

    # Check if the product already exists in the cart with status "pay yet"
    existing_item = cartCollection.find_one({"username": username, "productID": productID, "status": "pay yet"})
    
    if existing_item:
        # Update the quantity of the existing item
        new_quantity = existing_item["quantity"] + quantity
        cartCollection.update_one(
            {"_id": existing_item["_id"]},
            {"$set": {"quantity": new_quantity}}
        )
        return {"message": "Item quantity updated in cart", "new_quantity": new_quantity}
    else:
        # Add new cart item
        newCartItemData = CartItem(username=username, productID=productID, status="pay yet", quantity=quantity)
        cartCollection.insert_one(newCartItemData.model_dump())
        return {"message": "New item added to cart"}



# PUT update item quantity in cart
async def updateCart(username: str, productID: str, quantity: int):
    if not ObjectId.is_valid(productID):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    cartCollection.update_one(
        {"username": username, "productID": productID},
        {"$set": {"quantity": quantity}}
    )
    return {"message": "Cart updated successfully"}

async def updateItemStatus(itemID: str, status: str):
    if not ObjectId.is_valid(itemID):
        return None
    
    cartCollection.update_one(
        {"_id": ObjectId(itemID)},
        {"$set": {"status": status}}
    )
    return 1

# DELETE remove item from cart
async def removeFromCart(username: str, productID: str):
    if not ObjectId.is_valid(productID):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    cartCollection.find_one_and_delete(
        {"username": username, "productID": productID},
    )
    return {"message": "Item removed from cart"}

# POST payment for items in cart
async def checkoutCart(username: str):
    global checkoutCartID, kafkaMessages

    # Call service to get all items in cart which has `status` == "pay yet"
    cartItems = listSerial(cartCollection.find({"username": username, "status": "pay yet"}))
    
    if not cartItems:
        raise HTTPException(status_code=404, detail="No items in cart for checkout")
    
    # Send items to product service to check availability of items
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

    msg_dict: dict = {
        "id": f"c{checkoutCartID}",
        "opcode": define.OP_CHECKOUT_CART,
        "username": username,
        "items": []
    }

    checkoutCartID += 1

    for cartItem in cartItems:
        msg_dict["items"].append({"productID": cartItem["productID"], "quantity": cartItem["quantity"]})
    
    producer.send(config.KAFKA_TOPIC, json.dumps(msg_dict).encode("utf-8"))

    timeout = 2000 # 2000 miliseconds
    while(1):
        timeout -= 10
        if timeout <= 0:
            return {"message": "Cannot receive responsive from other service"}
        
        if(msg_dict["id"] in kafkaMessages):
            if kafkaMessages[msg_dict["id"]] == define.OP_CHECK_PRODUCT_QUANTITY_FAILED:
                return {"message": "Product is not enough", "opcode": define.OP_CHECK_PRODUCT_QUANTITY_FAILED}
            elif kafkaMessages[msg_dict["id"]] == define.OP_CHECK_USER_ACCOUNT_FAILED:
                return {"message": "Your account is not enough", "opcode": define.OP_CHECK_USER_ACCOUNT_FAILED}
            elif kafkaMessages[msg_dict["id"]] == define.OP_CHECK_USER_ACCOUNT_SUCCESS:
                # update item to paid
                for item in cartItems:
                    await updateItemStatus(item["id"], "paid")
                return {"message": "Success", "opcode": define.OP_CHECK_USER_ACCOUNT_SUCCESS}
        
        await asyncio.sleep(0.01)