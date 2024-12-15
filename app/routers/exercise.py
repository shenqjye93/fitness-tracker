from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path


import json

router = APIRouter()

class Exercise(BaseModel):
    id: int
    category: str = "exercise"
    name: str
    type: str 
    weight: float 
    
data_file = "data/data.json"

## call function to unpack data
def read_data():
    try:
        with open(data_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    
## call function to write/ update data
def write_data(data):
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)

@router.get("/exercises")
async def get_exercise():
    return read_data()

@router.get("/get-exercises/{exercise_id}")
async def get_exercise(exercise_id: str):
    exercises = read_data()
    if exercise_id not in exercises:
        raise HTTPException(status_code=404, detail="Error, exercise not found")
    
    exercise = exercises[exercise_id]
    
    if exercise["category"] == "exercise":
        return exercise
    else:
        raise HTTPException(status_code=404, detail="Error, exercise not found")
    
@router.post("/create-exercises/{exercise_id}")
async def create_exercise(exercise_id: str, exercise: Exercise):
    exercises = read_data()
    if exercise_id in exercises:
        return {"message": "Exercise Exists"}
    ## updates exercises data with new info
    exercises[exercise_id] = exercise.dict() #exercise model is not dict
    write_data(exercises)
    return exercises[exercise_id] 

@router.put("/create-exercises/{exercise_id}")
async def update_exercise(exercise_id: str, exercise: Exercise):
    exercises = read_data()
    if exercise_id not in exercises:
        raise HTTPException (status_code=404, detail= "Error, exercise not found")
    exercises[exercise_id] = exercise.dict() 
    write_data(exercises)
    return exercises[exercise_id] 

@router.delete("/delete-exercises/{exercise_id}")
async def delete_exercise(exercise_id: str):
    exercises = read_data()
    if exercise_id not in exercises:
        raise HTTPException (status_code=404, detail= "Error, exercise not found")
    else:
        del exercises[exercise_id]
        write_data(exercises)
        return {"detail": f"exercise {exercise_id} has been deleted"}


# @router.get("/exercises/")
# async def get_html():
#     html_file_path = Path("template/index.html")  # Specify your HTML file path
#     html_content = html_file_path.read_text(encoding="utf-8")
#     return HTMLResponse(content=html_content, status_code=200)

# @router.get("/dashboard/", response_class=HTMLResponse)
# async def get_dashboard():
#     html_file_path = Path("template/dashboard.html")  # Specify the dashboard HTML file path
#     html_content = html_file_path.read_text(encoding="utf-8")
#     return HTMLResponse(content=html_content, status_code=200)

# @router.get("/exp/", response_class=HTMLResponse)
# async def get_dashboard():
#     html_file_path = Path("template/exp.html")  # Specify the dashboard HTML file path
#     html_content = html_file_path.read_text(encoding="utf-8")
#     return HTMLResponse(content=html_content, status_code=200)