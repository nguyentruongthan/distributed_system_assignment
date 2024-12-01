def individualSerial(cartItem) -> dict:
    return {
        "id": str(cartItem['_id']),
        "username": str(cartItem['username']),
        "productID": cartItem['productID'],
        "status": cartItem['status'],
        "quantity": cartItem['quantity'],
    }

def listSerial(cartItems) -> list:
    return [individualSerial(cartItem) for cartItem in cartItems]