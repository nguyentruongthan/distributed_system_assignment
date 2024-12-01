def individualSerial(user) -> dict:
    return {
        "id": str(user['_id']),
        "username": str(user['username']),
        "account": user['account']
    }

def listSerial(users) -> list:
    return [individualSerial(user) for user in users]