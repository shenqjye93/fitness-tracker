from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pathlib import Path

import json

router = APIRouter()

class Metric(BaseModel):
    id: int
    category: str = "metrics"
    type: str
    level: int

data_file = "data/data.json"

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

@router.get("/metrics")
async def get_metric():
    return read_data()

@router.get("/get-metrics/{metrics_id}")
async def get_metric(metrics_id: str):
    metrics = read_data()
    if metrics_id not in metrics:
        raise HTTPException(status_code=404, detail="Error, metric not found")
    
    metric = metrics[metrics_id]
    
    if metric["category"] == "metric":
        return metric
    else:
        raise HTTPException(status_code=404, detail="Error, metric not found")
    
@router.post("/create-metrics/{metrics_id}")
async def create_metric(metrics_id: str, metric: Metric):
    metrics = read_data()
    if metrics_id in metrics:
        return {"message": "Metric Exists"}
    ## updates metrics data with new info
    metrics[metrics_id] = metric.dict() #metric model is not dict
    write_data(metrics)
    return metrics[metrics_id] 

@router.put("/create-metrics/{metrics_id}")
async def update_metric(metrics_id: str, metric: Metric):
    metrics = read_data()
    if metrics_id not in metrics:
        raise HTTPException (status_code=404, detail= "Error, metric not found")
    metrics[metrics_id] = metric.dict() 
    write_data(metrics)
    return metrics[metrics_id] 

@router.delete("/delete-metrics/{metrics_id}")
async def delete_metric(metrics_id: str):
    metrics = read_data()
    if metrics_id not in metrics:
        raise HTTPException (status_code=404, detail= "Error, metric not found")
    else:
        del metrics[metrics_id]
        write_data(metrics)
        return {"detail": f"metric {metrics_id} has been deleted"}


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
