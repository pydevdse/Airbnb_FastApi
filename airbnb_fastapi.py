import json
from datetime import date, datetime
from typing import Union

from fastapi import FastAPI
from airbnb_api import Airbnb

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/item_info/{item_id}")
async def read_item(item_id: int):
    return Airbnb().get_room_info(item_id)


@app.get("/item_info_price/{item_id}")
async def read_item(
    item_id: int,
    checkIn: date = datetime.now().date(),
    checkOut: date = date(
        year=datetime.now().date().year,
        month=datetime.now().date().month,
        day=datetime.now().date().day + 4,
    ),
):
    return Airbnb().get_room_info_price(item_id, checkIn, checkOut)


@app.get("/item_info_available/{item_id}")
async def read_item(item_id: int, month: int = datetime.now().month):
    return Airbnb().get_room_available(item_id, month)
