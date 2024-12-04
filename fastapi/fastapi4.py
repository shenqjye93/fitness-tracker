# Declare Request Example Data
from fastapi import FastAPI, Body
from pydantic import BaseModel

from typing import Annotated

app = FastAPI ()

class Item(BaseModel):
    name:str
    description: str | None = None
    price: float
    tax: float | None = None

    ## Extra JSON Schema data in Pydantic models
    ### a list of dict, in a dict (examples), in a dict (json_...)
    ### will be shown as an example schema 
    # model_config = {
    #     "json_schema_extra": {
    #         "examples": [
    #             {
    #                 "name": "Foo", 
    #                 "description": "nice item", 
    #                 "price": 35.4, 
    #                 "tax": 2.2
    #             }
    #         ]
    #     }
    # }

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = ({"item_id": item_id, "item": item})
    return results

@app.put("/items2/{item_id}")
async def update_item(
    *,
    item_id: int,
    item: Annotated[
        Item, 
        Body(
            ## use openapi_examples to fancy up openapi doc
            openapi_examples = {
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
        )
    ]
):
    results = {"item_id": item_id, "item": item}
    return results