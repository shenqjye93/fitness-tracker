from fastapi import FastAPI, Depends, HTTPException, status, Request, Response, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm #Keep this import
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from contextlib import contextmanager
from passlib.context import CryptContext
import sqlite3
import os
import secrets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'health_metrics.sqlite')
SECRET_KEY = secrets.token_urlsafe(32)

router = APIRouter()
app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY
)


class Exercise(BaseModel):
    id: int    
    user_id: int
    category: str = "exercise"
    name: str
    type: str
    weight: float

class BP(BaseModel):
    id: int
    user_id: int
    category: str = "metric"
    type: str
    systolic: int
    diasystolic: int
    pulse: int

class Glucose(BaseModel):
    id: int
    user_id: int    
    category: str = "metric"
    type: str
    level: int

class User(BaseModel):
    user_id: int

    class Config:
        from_attributes = True

class User_create(BaseModel):
    username: str       
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- Datebase Helper Functions ---
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    try:
        yield conn
    finally:
        conn.close()

def create_user(db, username, password_hash):
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO users_info (username, password_hash)
                       VALUES (?, ?)""",
                       (username, password_hash))
        db.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(status_code = 400, detail="Username already exists")
    
def get_user_by_username(db, username):
    cursor = db.cursor()
    cursor.execute("""SELECT *
                   FROM users_info
                   WHERE username = ?""",
                   (username,))
    return cursor.fetchone()

def get_user_by_id(db, user_id):
    cursor = db.cursor()
    cursor.execute("""SELECT user_id 
                   FROM users_info 
                   WHERE user_id = ?""", 
                   (user_id,))
    return cursor.fetchone()

def get_exercises_for_user(db, user_id, limit: int = 20):
    cursor = db.cursor()
    cursor.execute("""SELECT * 
                       FROM exercise_metrics 
                       WHERE user_id = ? 
                       LIMIT ?""", 
                       (user_id, limit))
    exercises_data = {}
    for row in cursor.fetchall():
        row_dict = dict(row)
        exercise_id = str(row_dict.pop('id'))
        exercises_data[exercise_id] = row_dict
    return exercises_data

def get_metrics_for_user(db, user_id, limit: int = 20):
    cursor = db.cursor()
    cursor.execute("""SELECT * 
                       FROM health_metrics 
                       WHERE user_id = ? 
                       LIMIT ?""", 
                       (user_id, limit))
    health_data = {}
    for row in cursor.fetchall():
        row_dict = dict(row)
        metrics_id = str(row_dict.pop('id'))
        health_data[metrics_id] = row_dict
    return health_data

def get_exercise_by_id(db, exercise_id, user_id):
    cursor = db.cursor()
    cursor.execute("""SELECT * 
                   FROM exercise_metrics 
                   WHERE id = ? AND user_id = ?""", 
                   (exercise_id, user_id))
    return cursor.fetchone()

def get_metric_by_id(db, metrics_id, user_id):
    cursor = db.cursor()
    cursor.execute("""SELECT * 
                   FROM health_metrics 
                   WHERE id = ? AND user_id = ?""", 
                   (metrics_id, user_id))
    return cursor.fetchone()

def insert_exercise(db, exercise: Exercise):
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO exercise_metrics (category, name, type, weight, id, user_id)
        VALUES (?, ?, ?, ?, ?, ?)""", 
        (exercise.category, 
         exercise.name, 
         exercise.type, 
         exercise.weight, 
         exercise.id, 
         exercise.user_id)) 
    db.commit()
    return cursor.lastrowid

def insert_bp(db, metric: BP):
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO health_metrics (category, type, systolic, diasystolic, pulse, id, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)""", 
        (metric.category, 
         metric.type, 
         metric.systolic, 
         metric.diasystolic, 
         metric.pulse, 
         metric.id, 
         metric.user_id)) 
    db.commit()
    return cursor.lastrowid

def insert_glucose(db, metric: Glucose):
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO health_metrics (category, type, level, id, user_id)
        VALUES (?, ?, ?, ?, ?)""", 
        (metric.category, 
         metric.type, 
         metric.level, 
         metric.id, 
         metric.user_id)) # Include user_id
    db.commit()
    return cursor.lastrowid

def update_exercise_db(db, exercise_id, exercise: Exercise, user_id):
    cursor = db.cursor()
    cursor.execute("""
        UPDATE exercise_metrics
        SET category = ?, name = ?, type = ?, weight = ?, id = ?, user_id = ?
        WHERE id = ? AND user_id = ?""", 
        (exercise.category, 
         exercise.name, 
         exercise.type, 
         exercise.weight, 
         exercise.id, 
         exercise.user_id, 
         exercise_id, 
         user_id))
    db.commit()

def update_bp_db(db, metrics_id, metric: BP, user_id):
    cursor = db.cursor()
    cursor.execute("""
        UPDATE health_metrics
        SET category = ?, type = ?, systolic = ?, diasystolic = ?, pulse = ?
        WHERE id = ? AND user_id = ?""", 
        (metric.category, 
         metric.type, 
         metric.systolic, 
         metric.diasystolic, 
         metric.pulse, 
         metrics_id, 
         user_id)) # Include user_id check
    db.commit()

def update_glucose_db(db, metrics_id, metric: Glucose, user_id):
    cursor = db.cursor()
    cursor.execute("""
        UPDATE health_metrics
        SET category = ?, type = ?, level = ?
        WHERE id = ? AND user_id = ?""", 
        (metric.category, 
         metric.type, 
         metric.level, 
         metrics_id, 
         user_id)) 
    db.commit()

def delete_metric_db(db, metrics_id, user_id):
    cursor = db.cursor()
    cursor.execute("""DELETE 
                   FROM health_metrics 
                   WHERE id = ? AND user_id = ?""", 
                   (metrics_id, user_id)) # Include user_id check
    db.commit()

def delete_exercise_db(db, exercise_id, user_id):
    cursor = db.cursor()
    cursor.execute("""DELETE 
                   FROM exercise_metrics 
                   WHERE id = ? AND user_id = ?""", 
                   (exercise_id, user_id)) # Include user_id check
    db.commit()

# --- Authentication Helper Functions ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
################ learn what this code does #################

def get_password_hash(password):
    return pwd_context.hash(password) # get the plain pwd from UserCreate model

async def get_current_user(request:Request):
    user_id = int(request.cookies.get("session_cookie"))
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user_id
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# --- Authentication Endpoints ---
@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def signup(user_create: User_create, response:Response):
    with get_db() as db:

        new_user = get_user_by_username(db, user_create.username)

        if new_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
        
        hashed_password = get_password_hash(user_create.password)
        user_id = create_user(db, user_create.username, hashed_password)
        response.set_cookie(key="user_id", value=str(user_id))
        user_info = get_user_by_id(db, user_id)

        return User(**user_info)
        
@router.post("/login", response_model=Token)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    with get_db() as db:

        user = get_user_by_username(db, form_data.username)

        if not user or not verify_password(form_data.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        response.set_cookie(key="session_cookie", value=int(user['user_id'])) 
        
        return Token(access_token="session_token_placeholder")

@router.post("/logout")
async def logout(response: Response):

    response.delete_cookie(key="user_id")

    return {"message": "Logged out"}

@router.get("/me", response_model=User)
async def read_users_me(request:Request, user_id: int = Depends(get_current_user)):
    with get_db() as db:

        user_info = get_user_by_id(db, user_id)
        
        if not user_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return User(**user_info)  


# --- Exercises Endpoints ---
@router.get("/exercises", response_model=dict)
async def get_exercise(current_user: int = Depends(get_current_user), limit: int=20):
    with get_db() as conn:

        return get_exercises_for_user(conn, current_user, limit)

@router.get("/get-exercises/{exercise_id}")
async def get_exercise(exercise_id: int, current_user: int = Depends(get_current_user)):
    with get_db() as conn:

        exercise = get_exercise_by_id(conn, exercise_id, current_user)
        if not exercise:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
       
        return dict(exercise)
    
@router.post("/create-exercises/{exercise_id}", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_exercise(exercise: Exercise, current_user: int = Depends(get_current_user)):
    with get_db() as conn:

        if exercise.user_id != current_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not authorized")
    
        if get_exercise_by_id(conn, exercise.id, current_user):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Exercise ID already exists for user")
        
        insert_exercise(conn, exercise.model_copy(update={'user_id': current_user}))

        # return get_exercise_by_id(conn, exercise.id, current_user)
        return {"message": "Exercise created successfully"}
    
@router.put("/create-exercises/{exercise_id}", response_model=dict)
async def update_exercise(exercise_id: int, exercise: Exercise, current_user: int = Depends(get_current_user)):
    with get_db() as conn:
        
        if exercise.id != exercise_id: 
            raise HTTPException(status_code=403, detail="Incorrect Exercise ID")
        

        if exercise.user_id != current_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not authorized")
        
        if not get_exercise_by_id(conn, exercise_id, current_user):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
        
        update_exercise_db(conn, exercise_id, exercise, current_user)
        
        return {"message": "Exercise updated successfully"}
    
@router.delete("/delete-exercises/{exercise_id}")
async def delete_exercise(exercise_id: int, current_user: int = Depends(get_current_user)):
    with get_db() as conn: 

        if not get_exercise_by_id(conn, exercise_id, current_user):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
        
        delete_exercise_db(conn, exercise_id, current_user)
        
        return {"detail": f"exercise {exercise_id} has been deleted"}
        
    
# --- Metric Endpoints (Protected) ---
@router.get("/metrics", response_model=dict)
async def get_metrics(current_user: int = Depends(get_current_user), limit: int = 20):
    with get_db() as conn: 

        return get_metrics_for_user(conn, current_user, limit)

@router.get("/get-metrics/{metrics_id}", response_model=dict)
async def get_metric(metrics_id: int, current_user: int = Depends(get_current_user)):
    with get_db() as conn: 

        metric = get_metric_by_id(conn, metrics_id, current_user)
        if not metric:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found")
       
        return dict(metric)

@router.post("/create-bp/{metrics_id}", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_bp(metric: BP, current_user: int = Depends(get_current_user)):
    with get_db() as conn:

        if metric.user_id != current_user: 
            raise HTTPException(status_code=403, detail="Not authorized to create BP for other users")
        
        if get_metric_by_id(conn, metric.id, current_user): # Check if metric id exists for user
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Metric ID already exists for user")
        
        insert_bp(conn, metric.model_copy(update={'user_id': current_user}))

        return {"message": "BP created successfully"}

@router.put("/create-bp/{metrics_id}", response_model=dict)
async def update_bp(metrics_id: int, metric: BP, current_user: int = Depends(get_current_user)):
    with get_db() as conn:

        if metric.id != metrics_id: 
            raise HTTPException(status_code=403, detail="Incorrect Metric ID")
        
        if metric.user_id != current_user: 
            raise HTTPException(status_code=403, detail="Not authorized to update BP")

        if not get_metric_by_id(conn, metrics_id, current_user):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found")
        
        update_bp_db(conn, metrics_id, metric.model_copy(update={'user_id': current_user}), current_user)

        return {"message": "BP updated successfully"}   

@router.post("/create-glucose/{metrics_id}", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_glucose(metric: Glucose, current_user: int = Depends(get_current_user)):
    with get_db() as conn:
        
        if metric.user_id != current_user: 
            raise HTTPException(status_code=403, detail="Not authorized")

        if get_metric_by_id(conn, metric.id, current_user): 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Metric ID already exists for user")
        
        insert_glucose(conn, metric.model_copy(update={'user_id': current_user}))

        return {"message": "Glucose created successfully"}

@router.put("/create-glucose/{metrics_id}", response_model=dict)
async def update_glucose(metrics_id: int, metric: Glucose, current_user: int = Depends(get_current_user)):
    with get_db() as conn:
        
        if metric.category == "bp":
            raise HTTPException(status_code=403, detail="Incorrect category")

        if metric.id != metrics_id: 
            raise HTTPException(status_code=403, detail="Incorrect Metric ID")
        
        if metric.user_id != current_user: 
            raise HTTPException(status_code=403, detail="Not authorized to update BP")
       
        if not get_metric_by_id(conn, metrics_id, current_user):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found")
        
        update_glucose_db(conn, metrics_id, metric.model_copy(update={'user_id': current_user}), current_user)

        return {"message": "Glucose updated successfully"}
        
@router.delete("/delete-metrics/{metrics_id}", response_model=dict)
async def delete_metric(metrics_id: int, current_user: int = Depends(get_current_user)):
    with get_db() as conn:
        
        if not get_metric_by_id(conn, metrics_id, current_user):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found")
        
        delete_metric_db(conn, metrics_id, current_user)

        return {"detail": f"metric {metrics_id} has been deleted"}
    

origins = ["*"]  # Allows all origins - VERY permissive, configure for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)