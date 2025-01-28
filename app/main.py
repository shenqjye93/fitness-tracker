from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import exercise_v2
from fastapi.responses import HTMLResponse
from pathlib import Path
from databases import Database

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'health_metrics.sqlite')}"

database = Database(DATABASE_URL)

app = FastAPI()

# css n js are static files
# use this code to serve those file when requested 
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(exercise_v2.router,  tags=["Health Metrics"])

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

@app.get("/")
async def get_html():
    html_file_path = Path("template/index-dashboard.html")  
    html_content = html_file_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/login/")
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

