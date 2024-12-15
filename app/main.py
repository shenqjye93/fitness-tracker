from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import exercise, metric
from fastapi.responses import HTMLResponse
from pathlib import Path


app = FastAPI()

# css n js are static files
# use this code to serve those file when requested 
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(exercise.router,  tags=["Exercises"])
app.include_router(metric.router,  tags=["Health Metrics"])

@app.get("/exercises/")
async def get_html():
    html_file_path = Path("template/index-ex.html")  # Specify your HTML file path
    html_content = html_file_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/metrics/")
async def get_html():
    html_file_path = Path("template/index-health.html")  # Specify your HTML file path
    html_content = html_file_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content, status_code=200)