import asyncio
from fastapi import FastAPI
import time 
from post_req import router
app=FastAPI()
app.include_router(router)
@app.get("/")
async def home():
    time.sleep(2)  # Simulate a delay of 2 seconds
    return {"message": "Welcome to the FastAPI application!"}

@app.post("/items/")
def create_item(item: dict):
    return {"item": item}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "name": f"Item {item_id}"}



async def databsestim():
    await asyncio.sleep(2)
    return {
        "message": "This is a test function simulating a database operation."
    }

@app.get("/users/{id}")
async def get_user(id: int):
    user = await databsestim()
    return user


