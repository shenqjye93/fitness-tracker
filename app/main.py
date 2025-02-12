from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import exercise_v3
# from routers import user_management
from starlette.middleware.sessions import SessionMiddleware # Import SessionMiddleware from fastapi.middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path
from databases import Database
import secrets
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'health_metrics.sqlite')}"
SECRET_KEY = secrets.token_urlsafe(32)

database = Database(DATABASE_URL)

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
)

# css n js are static files
# use this code to serve those file when requested 
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(exercise_v3.router,  tags=["Health Metrics"])
# app.include_router(user_management.router,  tags=["Login"])

@app.get("/exercises/")
async def get_html():
    html_file_path = Path("template/index-ex.html")  
    html_content = html_file_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/metrics/")
async def get_html():
    html_file_path = Path("template/index-health.html")  
    html_content = html_file_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/dashboard/")
async def get_html():
    html_file_path = Path("template/index-dashboard.html")  
    html_content = html_file_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/")
async def get_html():
    html_file_path = Path("template/index-login.html")  # Specify your HTML file path
    html_content = html_file_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content, status_code=200)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

origins = ["*"]  # Allows all origins - VERY permissive, configure for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)