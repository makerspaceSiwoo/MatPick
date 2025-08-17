from typing import Union
from fastapi import FastAPI

app = FastAPI()

# FAST API 공부용


@app.get("/")
def read_root():
    return {"Hello": "world"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
