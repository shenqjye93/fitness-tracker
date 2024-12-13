from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import exercise, metric

app = FastAPI()

# css n js are static files
# use this code to serve those file when requested 
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(exercise.router,  tags=["Exercises"])
app.include_router(metric.router,  tags=["Health Metrics"])