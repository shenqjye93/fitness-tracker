# JSON Compatible Encoder
## typically to convert a python data to fit json 
from datetime import datetime

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

fake_db = {}


class Item(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None

app = FastAPI()


@app.put("/items/{id}")
def update_item(id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    fake_db[id] = json_compatible_item_data
    return {"data": fake_db}

#---------------------------------------------------------------------

# Returning a direct response
## Return a Response
from fastapi.responses import JSONResponse

@app.put("/items/{id}")
def update_item(id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    return JSONResponse(content=json_compatible_item_data) # this is by default what happens

## Return a custom Response
from fastapi import FastAPI, Response

@app.get("/legacy/")
def get_legacy_data():
    data = """<?xml version="1.0"?>
    <shampoo>
    <Header>
        Apply shampoo here.
    </Header>
    <Body>
        You'll have to use soap here.
    </Body>
    </shampoo>
    """
    return Response(content=data, media_type="application/xml")

#---------------------------------------------------------------------

# Custom Response - HTML
## Using ORJSONResponse
from fastapi.responses import ORJSONResponse

@app.get("/items/", response_class=ORJSONResponse)
async def read_items():
    return ORJSONResponse([{"item_id": "Foo"}])

## HTML Response
### Example 1
from fastapi.responses import HTMLResponse

@app.get("/items_HTMLs/", response_class=HTMLResponse)
async def read_items():
    return """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """

### Example 2

@app.get("/items_HTMLs2/")
async def read_items():
    #store html code so that we can put inside our return response
    html_content = """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
        <div>
            LOLOL
        </div>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)