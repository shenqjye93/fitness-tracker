from enum import Enum
from fastapi import FastAPI

class ModelName(str, Enum):
        alexnet = "alexnet" # ModelName.alexnet, O: "alexnet"
        resnet = "resnet"
        lenet = "lenet"

app = FastAPI()


@app.get("/models/{model_name}")
                    #model_name: type, only items in enum defined earlier can be used
async def get_model(model_name: ModelName): 
    if model_name is ModelName.alexnet:
          return {
                "model_name" : model_name,
                "message" : "Deep Learning FTW!"
          }
    # enum.value shows "lenet"
    if model_name.value == "lenet" :
          return {
                "model_name" : model_name,
                "message" : "LeCNN all the images"
          }
    
    return {
          "model_name" : model_name,
          "message" : "Have some residuals"
    }


#get file_path
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
      return {
            "file_path" : file_path
      }

#---------------------------------------------------
#Query Parameters
## 1.limits
fake_items_db = [
      {"item_name": "Foo"},
      {"item_name": "Bar"},
      {"item_name": "Sam"}
]

@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10): # default items to show is 10, also we assign int datatype
      return fake_items_db[skip : skip + limit] # slice for number of items to show [start: stop]

## 2. Optional Parameters
@app.get("/items/{item_id}")
async def read_item(item_id: str, category: str | None = None):
    if category:
        return {"item_id": item_id, "category": category}
    return {"item_id": item_id}

## 3. Type conversion (update)
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "This is long"})
    return item # return only once, else the code stops at the first return

## 4. Multiple paths 
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, category: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if category:
        item.update({"category": category})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

## 5. Required query (needy)
@app.get("/test/{test_id}")
async def read_user_test(
    test_id: str, needy: str, skip: int = 0, limit: int | None = None
):
    test = {"test_id": test_id, "needy": needy, "skip": skip, "limit": limit}
    return test


#---------------------------------------------------
# Request body

from pydantic import BaseModel

## create data model
class Object(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

app = FastAPI()

## POST is used to send data
@app.post("/objects/")
async def create_object(object: Object):
    object_dict = object.dict()
    if object.tax:
        price_with_tax = object.price + object.tax
        object_dict.update({"price_with_tax":price_with_tax})
    return object_dict

## Request body + path parameters
@app.put("/objects/{object_id}")
async def update_item(object_id: int, object: Object):
    return {"object_id": object_id, **object.dict()} #** is used to unpack the dictionary