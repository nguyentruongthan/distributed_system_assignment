from fastapi import FastAPI, HTTPException
import httpx
import uvicorn

import config, define

app = FastAPI()

# Base URLs for services
BASE_URL_CART = f"http://{config.CART_URL}:{config.CART_PORT}"
BASE_URL_PRODUCTS = f"http://{config.PRODUCT_URL}:{config.PRODUCT_PORT}"
BASE_URL_USERS = f"http://{config.USER_URL}:{config.USER_PORT}"

# Helper function to handle HTTP requests
async def forward_request(method: str, url: str, data=None, params=None):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, url, json=data, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())

# Cart Routes
@app.get("/cart/{username}")
async def get_cart(username: str):
    return await forward_request("GET", f"{BASE_URL_CART}/cart/{username}")

@app.post("/cart/{username}/add")
async def add_to_cart(username: str, productID: str, quantity: int):
    return await forward_request("POST", f"{BASE_URL_CART}/cart/{username}/add", params={"productID": productID, "quantity": quantity})

@app.put("/cart/{username}/update")
async def update_cart(username: str, productID: str, quantity: int):
    return await forward_request("PUT", f"{BASE_URL_CART}/cart/{username}/update", params={"productID": productID, "quantity": quantity})

@app.delete("/cart/{username}/remove/{productID}")
async def remove_from_cart(username: str, productID: str):
    return await forward_request("DELETE", f"{BASE_URL_CART}/cart/{username}/remove/{productID}")

@app.post("/cart/{username}/checkout")
async def checkout(username: str):
    return await forward_request("POST", f"{BASE_URL_CART}/cart/{username}/checkout")

# Product Routes
@app.get("/products")
async def get_products():
    return await forward_request("GET", f"{BASE_URL_PRODUCTS}/products")

@app.get("/products/{productID}")
async def get_product(productID: str):
    return await forward_request("GET", f"{BASE_URL_PRODUCTS}/products/{productID}")

@app.post("/products")
async def add_product(product: dict):
    return await forward_request("POST", f"{BASE_URL_PRODUCTS}/products", data=product)

@app.put("/products/{productID}")
async def update_product(productID: str, product: dict):
    return await forward_request("PUT", f"{BASE_URL_PRODUCTS}/products/{productID}", data=product)

@app.put("/products/{productID}/increase")
async def increase_product_quantity(productID: str, amount: int):
    return await forward_request("PUT", f"{BASE_URL_PRODUCTS}/products/{productID}/increase", params={"amount": amount})

@app.put("/products/{productID}/decrease")
async def decrease_product_quantity(productID: str, amount: int):
    return await forward_request("PUT", f"{BASE_URL_PRODUCTS}/products/{productID}/decrease", params={"amount": amount})

@app.delete("/products/{productID}")
async def delete_product(productID: str):
    return await forward_request("DELETE", f"{BASE_URL_PRODUCTS}/products/{productID}")

# User Routes
@app.get("/users")
async def get_users():
    return await forward_request("GET", f"{BASE_URL_USERS}/users")

@app.get("/users/{username}")
async def get_user(username: str):
    return await forward_request("GET", f"{BASE_URL_USERS}/users/{username}")

@app.post("/users")
async def add_user(username: str):
    return await forward_request("POST", f"{BASE_URL_USERS}/users", data={"username": username})

@app.put("/users/{username}/increase/{amount}")
async def increase_user_account(username: str, amount: int):
    return await forward_request("PUT", f"{BASE_URL_USERS}/users/{username}/increase/{amount}")

@app.put("/users/{username}/decrease/{amount}")
async def decrease_user_account(username: str, amount: int):
    return await forward_request("PUT", f"{BASE_URL_USERS}/users/{username}/decrease/{amount}")

@app.delete("/users/{username}")
async def delete_user(username: str):
    return await forward_request("DELETE", f"{BASE_URL_USERS}/users/{username}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=config.GATEWAY_PORT, reload=True)