from fastapi import FastAPI, Query, Path
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
liste = ["toto", "tata"]


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@app.post("/items/")
async def create_item(item: Item):
    return item

@app.get("/library/{item_id}")
async def library(
    item_id : Annotated[str, Path(title="the id for search")],
    q : Annotated[str | None, Query(alias="add-q", title="A var for request")] = None
):  
    item = {"item_id" : item_id}
    if q:
        item.update({"q": q})
    return item
    