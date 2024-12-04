# Query Parameters and String Validations
from typing import Annotated, Literal
from fastapi import FastAPI, Query, Path
from pydantic import BaseModel, Field

app = FastAPI()

## Query parameters
@app.get("/items/")
async def read_items(
    #q: str | None = None):                                                 #1 | acts as or, so q can be str or empty
    #q: Annotated[str | None, Query(max_length=50)] = None):                #2a Additional validation (Query())
    #q: str | None = Query(default = None, max_length=50)):                 #2b non annotated syntax
    #q: Annotated[str | None, Query(max_length=50, min_length=3)] = None):  #3 More validations (min_length)
    #q: Annotated[str | None, Query(min_length=3, max_length=50, pattern="^fixedquery$") ] = None,): #4 regular expression (pattern), syntax for pattern, starts with '^' > 'exact value' > '$'
    #q: Annotated[str, Query(min_length=3)] = "fixedquery"):                #5 default values 
    #q: Annotated[str, Query(min_length=3)]):                               #6a q is required, without '=None'
    #q: Annotated[str, Query(min_length=3)] = ...):                         #6b q is required, using '= ...'
    q: Annotated[str | None, Query(min_length= 3)] = ...):                  #6c required can be 'None'
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

## Query parameter list (multiple values) - **Query() MUST be used**
@app.get("/items2/")
async def read_items(
    #q: Annotated[list[str] | None, Query()] = None): #1 multiple query can be used
    q: Annotated[list[str] | None, Query()] = ["diu","lei","lou","mou"]): #2 default query
    query_items = {"q": q}
    return query_items

## Declare more metadata - adding more info about parameter
@app.get("/items3/")
async def read_items(
#     q: Annotated[
#         str | None, 
#         Query(
#             title="YO WASSUP", 
#             min_length=3
#             ),
#         ] = None,
# ): #1 adding title, can only check in http://127.0.0.1:8000/openapi.json
    
#     q: Annotated[
#         str | None,
#         Query(
#             title="Query string",
#             description="Query string for the items to search in the database that have a good match",
#             min_length=3,
#         ),
#     ] = None,
# ): #2 add description

    # q: Annotated[str | None, Query(alias="item-query")] = None): #3 add alias for q, query http://127.0.0.1:8000/items3/?item-query=dasdsa 
    
    q: Annotated[
        str | None,
        Query(
            alias="item-query",
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            min_length=3,
            max_length=50,
            pattern="^fixedquery$",
            deprecated=True, #add this part
        ),
    ] = None,
): #4 deprecating parameters, no use liao 
    results = {"items3": [{"item3_id": "Foo"}, {"item3_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

## Exclude parameters from OpenAPI, wont be in the documentation
## used for a few reasons -- note in excalidraw
@app.get("/items4/")
async def read_items(
    hidden_query: Annotated[str | None, Query(include_in_schema=False)] = None,
):
    if hidden_query:
        return {"hidden_query": hidden_query}
    else:
        return {"hidden_query": "Not found"}
    
#---------------------------------------------------------------------

#Query Parameter Models

class FilterParams(BaseModel):

    model_config = {"extra": "forbid"} # sends error msg if data apart from the model is given

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []

@app.get("/items_model/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query

#---------------------------------------------------------------------

#Path Parameters and Numeric Validations

    #endpoint
@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get")], #title adds to documentation
    q : Annotated[str | None, Query(alias="item-query")] = None,
):
    results = {"item_id": item_id}
    if q: 
        results.update({"q": q})
    return results

## special case, use "*" - if ddly
## but to be safe, use Annotated[] whenever possible

## Number validations
@app.get("/items2/{item_id}")
async def read_item(
    #item_id: Annotated[int, Path(title="The ID of the item to get", ge=1)], #1. ge, '>='
    item_id: Annotated[int, Path(title="The ID of the item to get", gt=0, le=1000)], #2. gt, '>', le, '<='
    q: Annotated[str | None, Query(alias="item-query", title="why am i doing this")],
    size: Annotated[float, Query(gt=0, lt=10.5)] #3 can use float too, lt, '<'
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if size:
        results.update({"size": size})
    return results


