from fastapi import FastAPI, Path, HTTPException
from typing import Optional,Dict
from pydantic import BaseModel

app = FastAPI()


class Exercise(BaseModel):
    name: str
    weight: float
    type: str

exercises: Dict [int, Exercise] = {
    1: Exercise(id=1, name="Push ups", weight=55, type="Bodyweight"),
    2: Exercise(id=2, name="Bench press", weight=100, type="Barbell"),
}


@app.get("/get-exercises/{exercise_id}")
async def get_exercise(exercise_id: int = Path(description = "exercise ID")):
    if exercise_id not in exercises:
        raise HTTPException(status_code=404, detail="exercise not found")
    return exercises[exercise_id]

@app.get("/get-exercise-name/{exercise_id}")
async def get_exercise(*, exercise_id: int, name: Optional[str] = None):
    if exercise_id in exercises:
        exercises_value = exercises[exercise_id]
        if name is None or exercises_value.name == name:
            return exercises_value
    return {"Data": "Not Found"}

@app.post("/create-exercises/{exercise_id}")
async def create_exercise(exercise_id: int, exercise:Exercise):
    if exercise_id in exercises:
        return {"Error": "exercise exists"}
    exercises[exercise_id] = exercise
    return exercises[exercise_id]

@app.put("/update-exercises/{exercise_id}")
async def update_exercise(exercise_id: int, exercise:Exercise):
    if exercise_id in exercises:
        exercises[exercise_id] = exercise 
        return exercise 
    else:
        return HTTPException(status_code=404, detail= "exercise not found")
    
@app.delete("/delete-exercise/{exercise_id}")
async def delete_exercise(exercise_id: int):
    if exercise_id in exercises:
        del exercises[exercise_id] 
        return {"detail": f"exercise {exercise_id} has been deleted"}
    else:
        return HTTPException(status_code=404, detail = "exercise not found")