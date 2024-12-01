from fastapi import HTTPException
import json

from database import userCollection
from model import User
from schema import listSerial, individualSerial
import config, define
from kafka_producer import producer

async def getUsers():
    return listSerial(userCollection.find())

async def getUser(username: str):
    existingUser = userCollection.find_one({"username": username})
    if not existingUser:
        raise HTTPException(status_code=404, detail="User not found")
    
    return individualSerial(existingUser)

async def postUser(username: str):
    # Check if the user already exists
    existingUser = userCollection.find_one({"username": username})
    if existingUser:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Proceed to insert if the user does not exist
    newUserData: User = User(username = username, account = 0)
    newUser = userCollection.insert_one(newUserData.model_dump())
    if not newUser.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to add user")
    
    return {"message": "User added successfully", "id": str(newUser.inserted_id)}


async def deleteUser(username: str):
    deletedProduct = userCollection.find_one_and_delete({"username": username})
    if not deletedProduct:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

async def increaseUserAccount(username: str, amount: int):
    # Increase the user's account balance
    updatedUser = userCollection.find_one_and_update(
        {"username": username},
        {"$inc": {"account": amount}},  # Increment the 'account' field by 'amount'
        return_document=True
    )
    
    if not updatedUser:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"Refund successful, {amount} added to user's account"}

async def decreaseUserAccount(username: str, amount: int):
    # Decrease the user's account balance
    user = userCollection.find_one({"username": username})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_balance = user.get("account", 0)
    
    # Check if the user has enough balance
    if current_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    updatedUser = userCollection.find_one_and_update(
        {"username": username},
        {"$inc": {"account": -amount}},  # Decrement the 'account' field by 'amount'
        return_document=True
    )
    
    if not updatedUser:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"Deduction successful, {amount} deducted from user's account"}



async def checkoutCart(data: dict):
    print("checkout cart")
    username = data["username"] 
    totalPrice = data["totalPrice"]
    # get user
    user: dict = await getUser(username)

    if not user:
        data["opcode"] = define.OP_CHECK_USER_ACCOUNT_FAILED
        data["userInvalid"] = True
        producer.send(config.KAFKA_TOPIC, json.dumps(data).encode("utf-8"))
        print(f"User {username} does not exist")
        return

    # check user account
    if user["account"] < totalPrice:
        data["opcode"] = define.OP_CHECK_USER_ACCOUNT_FAILED
        producer.send(config.KAFKA_TOPIC, json.dumps(data).encode("utf-8"))
        print(f"User {username} has {user['account']} but require {totalPrice}")
        return
    
    # decrease user account
    await decreaseUserAccount(username, totalPrice)
    data["opcode"] = define.OP_CHECK_USER_ACCOUNT_SUCCESS
    producer.send(config.KAFKA_TOPIC, json.dumps(data).encode("utf-8"))