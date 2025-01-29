from fastapi import FastAPI, Depends, HTTPException, status, Request, Response, APIRouter 
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse, RedirectResponse
# from fastapi_sessions.backends.implementations import InMemoryBackend
# from fastapi_sessions.session_verifier import SessionVerifier
# from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from pydantic import BaseModel
from contextlib import contextmanager
import sqlite3
import hashlib
import uuid
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'health_metrics.sqlite')

router = APIRouter()

# cookie_params = CookieParameters()
# cookie = SessionCookie(
#     cookie_name="session_cookie", 
#     identifier="general_verifier", 
#     auto_error=True, 
#     secret_key="your-secret-key", 
#     cookie_params=cookie_params
#     )
# backend = InMemoryBackend[str, uuid.UUID]()

class User(BaseModel):
    username: str
    password: str  

class SessionData(BaseModel):
    username: str

# class BasicVerifier(SessionVerifier[str, SessionData]):
#     def __init__(self):
#         super().__init__(
#             identifier="general_verifier",
#             auto_error=True,
#             backend=backend,
#             auth_http_exception=HTTPException(status_code=403, detail="Invalid session"),
#         )

# verifier = BasicVerifier()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    try:
        yield conn
    finally:
        conn.close()
        
#For testing
@router.get("/users")
async def get_users(limit: int=20):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT * 
                       FROM users_info
                       LIMIT ?""",
                       (limit,))

        user_dict = {}
        for row in cursor.fetchall():
            row_dict = dict(row)
            user_id = str(row_dict.pop('id'))  
            user_dict[user_id] = row_dict

        return user_dict

@router.post("/signup")
async def signup(user: User):
    with get_db() as conn:
        cursor = conn.cursor()
        hashed_password = hash_password(user.password)
        try:
            cursor.execute("INSERT INTO users_info (username, password) VALUES (?, ?)", 
                           (user.username, hashed_password)
            )
            conn.commit()
            return {"message": "User created successfully"}
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Username already exists")
        
@router.post("/login")
async def login(user: User, response: Response):
    with get_db() as conn:
        cursor = conn.cursor()
        hashed_password = hash_password(user.password)
        cursor.execute("SELECT id, username FROM users_info WHERE username = ? AND password = ?", 
                       (user.username, hashed_password)
        )
        db_user = cursor.fetchone()
        
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create session
        # session_id = str(uuid.uuid4())
        # session_data = SessionData(username=user.username)
        # await backend.create(session_id, session_data)
        # cookie.attach_to_response(response, session_id)
        # return {"message": "Login successful"}
    
# @router.post("/logout")
# async def logout(request: Request, response: Response, session_id: str = Depends(cookie)):
    # await backend.delete(session_id)
    # cookie.delete_from_response(response)
    # return {"message": "Logout successful"}    

