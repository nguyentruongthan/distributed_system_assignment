def individualSerial(product) -> dict:
    if not product: return None
    return {
        "id": str(product['_id']),
        "name": str(product['name']),
        "price": product['price'],
        "quantity": product['quantity'],
    }

def listSerial(products) -> list:
    return [individualSerial(product) for product in products]