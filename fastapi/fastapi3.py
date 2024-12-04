# Body - Multiple Parameters
from typing import Annotated, List, Union

from fastapi import FastAPI, Path, Body
from pydantic import BaseModel, Field, HttpUrl  

app = FastAPI()

## Example 1 requesting item as body parameter
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float 
    tax: float | None = None

@app.put("/items/{item_id}")
async  def update_item(
    item_id: Annotated[int, Path(title="The ID of the item", ge=0, le=1000)],
    q: str | None = None,
    item: Item | None = None
):
    results = {"item_id": item_id}
    if q: 
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results

## Example 2 multiple request body
    #structure for user request body
class User(BaseModel):
    username: str
    full_name: str | None = None

@app.put("/items2/{item_id}")
async def update_item(
    item_id: int, item: Item, user: User, importance: Annotated[int, Body()]
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results

## Example 3 multiple body parameters & query
@app.put("/items3/{item_id}")
async def update_item(
    *,
    item_id: int ,
    item: Item,
    user: User,
    importance: Annotated[int, Body(gt=0)],
    q: str | None = None, 
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results

## Example 4 embed a single body parameter, "item: Item = Body(embed=True)"
@app.put("/items4/{item_id}")
async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
    results = {"item_id": item_id, "item": item}
    return results

#---------------------------------------------------------------------

# Body - Fields
## Fields is used to validate the model attributes
## Fields works the same way as Query or Path, has all the same syntax
class Item_Field(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None


@app.put("/items5/{item_id}")
async def update_item(item_id: int, item: Annotated[Item_Field, Body(embed=True)]):
    results = {"item_id": item_id, "item": item}
    return results

#---------------------------------------------------------------------

# Body - Nested Models 
## list fields
class Image(BaseModel):
    #url: str       #1 check for string data for url
    url: HttpUrl    #2 check for valid URL data for url
    name: str

class Item_Nested(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    #tags: list = []            #1 define tags to be subtype without element type
    #tags: List[str] = []       #2 use List module to declare type, a list of strings
    tags: set[str] = set()      #3 Set types, to ensure requests are unique items
    #image: Image | None = None         #1 Image as a submodel class
    images: list[Image] | None = None   #2 Image submodel expects a list

@app.put("/items6/{item_id}")
async def update_item(item_id: int, item: Item_Nested):
    results = {"item_id": item_id, "item": item}
    return results

## deeply nested models - inception
class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item_Nested]

@app.put("/offers/")
async def create_offer(offer: Offer):
    return offer

## bodies of pure lists
@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images

## bodies of arbitrary 'dict's
@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]):
    return weights
