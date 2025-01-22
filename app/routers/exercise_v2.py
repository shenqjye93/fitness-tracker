from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import contextmanager
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.path.join(BASE_DIR, 'data', 'health_metrics.sqlite')


router = APIRouter()


class Exercise(BaseModel):
    id: int    
    # user_id: int
    category: str = "exercise"
    name: str
    type: str
    weight: float

class BP(BaseModel):
    id: int
    # user_id: int
    category: str = "metric"
    type: str
    systolic: int
    diasystolic: int
    pulse: int

class Glucose(BaseModel):
    id: int
    # user_id: int    
    category: str = "metric"
    type: str
    level: int

class User_info(BaseModel):
    id: int
    username: str
    password: str

# Database connection context manager
@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    try:
        yield conn
    finally:
        conn.close()


@router.get("/exercises")
async def get_exercise(limit: int=20):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM exercise_metrics 
                       LIMIT ?""",
                       (limit,))

        exercises_dict = {}
        for row in cursor.fetchall():
            row_dict = dict(row)
            exercise_id = str(row_dict.pop('id'))  
            exercises_dict[exercise_id] = row_dict

        return exercises_dict
    
@router.get("/metrics")
async def get_metric(limit: int=20):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT * 
                       FROM health_metrics
                       LIMIT ?""",
                       (limit,))

        health_dict = {}
        for row in cursor.fetchall():
            row_dict = dict(row)
            metrics_id = str(row_dict.pop('id'))  
            health_dict[metrics_id] = row_dict

        return health_dict

@router.get("/get-exercises/{exercise_id}")
async def get_exercise(exercise_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM exercise_metrics WHERE id = ?",
            (exercise_id,)
        )
        exercise = cursor.fetchone()
        
        if not exercise:
            raise HTTPException(
                status_code=404,
                detail="Error, exercise not found"
            )
        
        return dict(exercise)
    
@router.post("/create-exercises/{exercise_id}")
async def create_exercise(exercise: Exercise):
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if similar exercise exists
        cursor.execute("""
            SELECT id FROM exercise_metrics 
            WHERE id = ?
        """, (exercise.id,))
        
        if cursor.fetchone():
            return {"message": "Exercise Exists"}
        
        # Insert new exercise
        cursor.execute("""
            INSERT INTO exercise_metrics 
            (category, name, type, weight, id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            exercise.category,
            exercise.name,
            exercise.type,
            exercise.weight,
            exercise.id
        ))
        
        conn.commit()
        
        # Return the created exercise
        cursor.execute(
            "SELECT * FROM exercise_metrics WHERE id = ?",
            (cursor.lastrowid,)
        )
        return dict(cursor.fetchone())
    
@router.get("/get-metrics/{metrics_id}")
async def get_metric(metrics_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM health_metrics WHERE id = ?",
            (metrics_id,)
        )
        metric = cursor.fetchone()
        
        if not metric:
            raise HTTPException(
                status_code=404,
                detail="Error, metric not found"
            )
        
        return dict(metric)

@router.put("/create-exercises/{exercise_id}")
async def update_exercise(exercise_id: int, exercise: Exercise):
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if exercise exists
        cursor.execute(
            "SELECT id FROM exercise_metrics WHERE id = ?",
            (exercise_id,)
        )
        
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Error, exercise not found"
            )
        
        # Update exercise
        cursor.execute("""
            UPDATE exercise_metrics 
            SET category = ?, name = ?, type = ?, weight = ?
            WHERE id = ?
        """, (
            exercise.category,
            exercise.name,
            exercise.type,
            exercise.weight,
            exercise_id
        ))
        
        conn.commit()
        
        # Return updated exercise
        cursor.execute(
            "SELECT * FROM exercise_metrics WHERE id = ?",
            (exercise_id,)
        )
        return dict(cursor.fetchone())
    
@router.post("/create-bp/{metrics_id}")
async def create_bp(metric: BP):
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if similar metric exists
        cursor.execute("""
            SELECT id FROM health_metrics 
            WHERE id = ?
        """, (metric.id,))
        
        if cursor.fetchone():
            return {"message": "BP Exists"}
        
        # Insert new metric
        cursor.execute("""
            INSERT INTO health_metrics 
            (category, type, systolic, diasystolic, pulse, id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            metric.category,
            metric.type,
            metric.systolic,
            metric.diasystolic,
            metric.pulse,
            metric.id
        ))
        
        conn.commit()
        
        # Return the created metric
        cursor.execute(
            "SELECT * FROM health_metrics WHERE id = ?",
            (cursor.lastrowid,)
        )
        return dict(cursor.fetchone())

@router.put("/create-bp/{metrics_id}")
async def update_bp(metrics_id: int, metric: BP):
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if metric exists
        cursor.execute(
            "SELECT id FROM health_metrics WHERE id = ?",
            (metrics_id,)
        )
        
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Error, metric not found"
            )
        
        # Update metric
        cursor.execute("""
            UPDATE health_metrics 
            SET category = ?, type = ?, systolic = ?, diasystolic = ?, pulse = ? 
            WHERE id = ?
        """, (
            metric.category,
            metric.type,
            metric.systolic,
            metric.diasystolic,
            metric.pulse,
            metrics_id
        ))
        
        conn.commit()
        
        # Return updated metric
        cursor.execute(
            "SELECT * FROM health_metrics WHERE id = ?",
            (metrics_id,)
        )
        return dict(cursor.fetchone())
    
@router.post("/create-glucose/{metrics_id}")
async def create_glucose(metric: Glucose):
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if similar metric exists
        cursor.execute("""
            SELECT id FROM health_metrics 
            WHERE id = ?
        """, (metric.id,))
        
        if cursor.fetchone():
            return {"message": "BP Exists"}
        
        # Insert new metric
        cursor.execute("""
            INSERT INTO health_metrics 
            (category, type, level, id)
            VALUES (?, ?, ?, ?)
        """, (
            metric.category,
            metric.type,
            metric.level,
            metric.id
        ))
        
        conn.commit()
        
        # Return the created metric
        cursor.execute(
            "SELECT * FROM health_metrics WHERE id = ?",
            (cursor.lastrowid,)
        )
        return dict(cursor.fetchone())

@router.put("/create-glucose/{metrics_id}")
async def update_glucose(metrics_id: int, metric: Glucose):
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if metric exists
        cursor.execute(
            "SELECT id FROM health_metrics WHERE id = ?",
            (metrics_id,)
        )
        
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Error, metric not found"
            )
        
        # Update metric
        cursor.execute("""
            UPDATE health_metrics 
            SET category = ?, type = ?, level = ? 
            WHERE id = ?
        """, (
            metric.category,
            metric.type,
            metric.level,
            metric.id
        ))
        
        conn.commit()
        
        # Return updated metric
        cursor.execute(
            "SELECT * FROM health_metrics WHERE id = ?",
            (metrics_id,)
        )
        return dict(cursor.fetchone())    

@router.delete("/delete-metrics/{metrics_id}")
async def delete_metric(metrics_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if metric exists
        cursor.execute(
            "SELECT id FROM health_metrics WHERE id = ?",
            (metrics_id,)
        )
        
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Error, metric not found"
            )
        
        # Delete metric
        cursor.execute(
            "DELETE FROM health_metrics WHERE id = ?",
            (metrics_id,)
        )
        
        conn.commit()
        
        return {
            "detail": f"metric {metrics_id} has been deleted"
        }

@router.delete("/delete-exercises/{exercise_id}")
async def delete_exercise(exercise_id: int):

    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if exercise exists
        cursor.execute(
            "SELECT id FROM exercise_metrics WHERE id = ?",
            (exercise_id,)
        )
        
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Error, exercise not found"
            )
        
        # Delete exercise
        cursor.execute(
            "DELETE FROM exercise_metrics WHERE id = ?",
            (exercise_id,)
        )
        
        conn.commit()
        
        return {
            "detail": f"exercise {exercise_id} has been deleted"
        }
    
@router.get("/get-userinfo/{user_id}")
async def get_user(user_id: int, user_info: User_info):
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users_info WHERE id = ? ", 
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Error, user not found"
            )
        
        return dict(user)


@router.post("/create-userinfo/{user_id}")
async def create_user(user_info: User_info):
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_info (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """)

        cursor.execute("""
            SELECT * FROM users_info 
            WHERE id = ?
        """, (user_info.id,))

        if cursor.fetchone():
            return {"message" : "User exists"}

        cursor.execute("""
            INSERT INTO users_info
            (id, username, password)
            VALUES(?, ?, ?)
            """,(
                user_info.id,
                user_info.username,
                user_info.password
            )) 
        
        conn.commit()

        cursor.execute(
            "SELECT * FROM users_info WHERE id = ?",
            (cursor.lastrowid,)
        )
        return dict(cursor.fetchone())

@router.put("/create-userinfo/{user_id}")
async def update_user(user_id: int, user_info: User_info):
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id FROM users_info WHERE id = ?",
            (user_id,)
        )
        
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Error, user not found"
            )
        
        # Update metric
        cursor.execute("""
            UPDATE users_info 
            SET username = ?, password = ? 
            WHERE id = ?
        """, (
                user_info.username,
                user_info.password,
                user_id
        ))
        
        conn.commit()
        
        # Return updated metric
        cursor.execute(
            "SELECT * FROM users_info WHERE id = ?",
            (user_id,)
        )
        return dict(cursor.fetchone())
    
@router.delete("/create-userinfo/{user_id}")
async def delete_user(user_id: int):

    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if exercise exists
        cursor.execute(
            "SELECT id FROM users_info WHERE id = ?",
            (user_id,)
        )
        
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Error, User not found"
            )
        
        # Delete exercise
        cursor.execute(
            "DELETE FROM users_info WHERE id = ?",
            (user_id,)
        )
        
        conn.commit()
        
        return {
            "detail": f"user {user_id} has been deleted"
        }