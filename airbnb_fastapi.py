import json
from datetime import date
from typing import Union

from fastapi import FastAPI
from airbnb_api import Airbnb

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/item_info/{item_id}")
async def read_item(item_id: int):
    return Airbnb().get_room_info(item_id)  # {"Item info":Airbnb().get_room_info(item_id)} # {"item_id": item_id, "q": q} #


@app.get("/item_info_price/{item_id}")
async def read_item(item_id: int):
    return Airbnb().get_room_info_price(item_id)


@app.get("/item_info_available/{item_id}")
async def read_item(item_id: int, month: int = None ,from_date: date = None, to_date: date = None):
    return Airbnb().get_room_available(item_id, month, from_date, to_date)